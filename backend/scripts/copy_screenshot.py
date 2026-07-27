import shutil
from pathlib import Path

src = Path(__file__).resolve().parent.parent.parent / ".gemini/antigravity-ide/brain/48a9146d-a4d3-4792-9be8-affbe0aae4b4/media__1785153900360.png"
if not src.exists():
    # Fallback search in brain dir
    brain_dir = Path("/home/Krishna-Singh/.gemini/antigravity-ide/brain/48a9146d-a4d3-4792-9be8-affbe0aae4b4")
    matches = list(brain_dir.glob("media__*.png"))
    if matches:
        src = matches[-1]

dest_dir = Path(__file__).resolve().parent.parent.parent / "docs"
dest_dir.mkdir(exist_ok=True)
dest = dest_dir / "equityforge_demo.png"

if src.exists():
    shutil.copyfile(src, dest)
    print(f"Successfully copied {src} to {dest}")
else:
    print(f"Source file not found: {src}")
