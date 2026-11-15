import json
from pathlib import Path
from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from consoles.models import Manufacturer, Console


class Command(BaseCommand):
    help = "Seeds manufacturers, consoles, and uploads images to Cloudinary"

    def _attach_image(self, instance, field_name, rel_path, images_dir):
        current_file = getattr(instance, field_name)
        if not rel_path or current_file:
            return

        full_path = images_dir / rel_path
        if full_path.exists():
            with open(full_path, "rb") as f:
                current_file.save(full_path.name, File(f), save=True)
        else:
            self.stderr.write(self.style.WARNING(f"Missing image file: {full_path}"))

    def handle(self, *args, **options):
        seed_dir = Path(settings.BASE_DIR) / "seed_data"
        images_dir = seed_dir / "images"
        json_path = seed_dir / "console.json"

        data = json.loads(json_path.read_text(encoding="utf-8"))

        for item in data.get("manufacturers", []):
            logo_rel = item.pop("logo_file", None)
            manuf, _ = Manufacturer.objects.update_or_create(slug=item["slug"], defaults=item)
            self._attach_image(manuf, "logo", logo_rel, images_dir)

        for item in data.get("consoles", []):
            image_rel = item.pop("image_file", None)
            item["manufacturer"] = Manufacturer.objects.get(slug=item.pop("manufacturer_slug"))
            console, _ = Console.objects.update_or_create(slug=item["slug"], defaults=item)
            self._attach_image(console, "image", image_rel, images_dir)

        self.stdout.write(self.style.SUCCESS("consoleDB seeded successfully."))
