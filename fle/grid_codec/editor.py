"""
Interactive blueprint editor.

Run: uv run python -m fle.grid_codec.editor

Commands:
  paste <string>                        Paste a Factorio blueprint string (copy from game)
  place <entity> <x> <y> [direction]   Place an entity (direction: up/right/down/left, default: right)
  remove <index>                        Remove entity by index
  list                                  Show all placed entities
  show                                  Display the grid (machine + human side by side)
  clear                                 Remove all entities
  save <name>                           Save blueprint to blueprints/handcrafted/ as JSON
  load <path>                           Load a blueprint JSON
  entities [filter]                     List available entity names (optional substring filter)
  undo                                  Undo last placement
  label <text>                          Set blueprint label
  desc <text>                           Set blueprint description
  tags <tag1> <tag2> ...                Set tags
  help                                  Show this help
  quit                                  Exit

Shortcuts: p=place, v=paste, s=show, ls=list, rm=remove, u=undo, e=entities
"""

from __future__ import annotations

import json
import readline  # noqa: F401 — enables arrow keys + history in input()
import sys
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt

from fle.grid_codec.encoder import EntitySpec, BoundingBox, encode
from fle.grid_codec.decoder import decode
from fle.grid_codec.visualize import grid_to_machine, grid_to_human
from fle.grid_codec.schema import ENTITY_REGISTRY

DIR_MAP = {
    "up": 0, "u": 0, "n": 0, "north": 0, "0": 0,
    "right": 4, "r": 4, "e": 4, "east": 4, "4": 4,
    "down": 8, "d": 8, "s": 8, "south": 8, "8": 8,
    "left": 12, "l": 12, "w": 12, "west": 12, "12": 12,
}

DIR_NAMES = {0: "up", 4: "right", 8: "down", 12: "left"}


class BlueprintEditor:
    def __init__(self):
        self.entities: list[EntitySpec] = []
        self.undo_stack: list[list[EntitySpec]] = []
        self.label = ""
        self.description = ""
        self.tags: list[str] = []
        self.fig = None
        self.data_dir = "data/2.0"

    def _save_undo(self):
        self.undo_stack.append([EntitySpec(e.name, e.x, e.y, e.direction) for e in self.entities])

    def cmd_place(self, args: list[str]):
        if len(args) < 3:
            print("Usage: place <entity> <x> <y> [direction]")
            return

        name = args[0]
        if not ENTITY_REGISTRY.has_name(name):
            # Try fuzzy match
            matches = [n for n in ENTITY_REGISTRY.names() if name in n]
            if len(matches) == 1:
                name = matches[0]
                print(f"  -> matched: {name}")
            elif matches:
                print(f"  Ambiguous. Matches: {', '.join(matches[:10])}")
                return
            else:
                print(f"  Unknown entity '{name}'. Use 'entities' to list available names.")
                return

        try:
            x, y = int(args[1]), int(args[2])
        except ValueError:
            print("  x and y must be integers")
            return

        direction = 4  # default: right
        if len(args) > 3:
            d = args[3].lower()
            if d in DIR_MAP:
                direction = DIR_MAP[d]
            else:
                print(f"  Unknown direction '{d}'. Use: up/right/down/left")
                return

        info = ENTITY_REGISTRY.from_name(name)
        self._save_undo()
        self.entities.append(EntitySpec(name=name, x=x, y=y, direction=direction))
        print(f"  [{len(self.entities)-1}] {name} ({info.width}x{info.height}) at ({x},{y}) facing {DIR_NAMES[direction]}")

    def cmd_remove(self, args: list[str]):
        if not args:
            print("Usage: remove <index>")
            return
        try:
            idx = int(args[0])
        except ValueError:
            print("  Index must be an integer")
            return
        if 0 <= idx < len(self.entities):
            self._save_undo()
            removed = self.entities.pop(idx)
            print(f"  Removed [{idx}] {removed.name} at ({removed.x},{removed.y})")
        else:
            print(f"  Invalid index. Range: 0-{len(self.entities)-1}")

    def cmd_list(self, _args: list[str]):
        if not self.entities:
            print("  (empty)")
            return
        for i, e in enumerate(self.entities):
            info = ENTITY_REGISTRY.from_name(e.name)
            print(f"  [{i:3d}] {e.name:30s} ({e.x:4d},{e.y:4d}) {DIR_NAMES.get(e.direction, '?'):5s}  {info.width}x{info.height}")

    def cmd_show(self, _args: list[str]):
        if not self.entities:
            print("  Nothing to show. Place some entities first.")
            return

        bounds = BoundingBox.from_entities(self.entities, padding=2)
        grid = encode(self.entities, bounds=bounds)

        machine_img = grid_to_machine(grid, scale=48)
        human_img = grid_to_human(grid, data_dir=self.data_dir, scale=48)

        if self.fig is not None:
            plt.close(self.fig)

        self.fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

        ax1.imshow(machine_img)
        ax1.set_title("Machine mode")
        ax1.axis("off")

        ax2.imshow(human_img)
        ax2.set_title(f"Human mode — {self.label or '(untitled)'}")
        ax2.axis("off")

        plt.tight_layout()
        plt.ion()
        plt.show()
        plt.pause(0.1)

    def cmd_clear(self, _args: list[str]):
        self._save_undo()
        self.entities.clear()
        print("  Cleared all entities.")

    def cmd_undo(self, _args: list[str]):
        if not self.undo_stack:
            print("  Nothing to undo.")
            return
        self.entities = self.undo_stack.pop()
        print(f"  Undone. {len(self.entities)} entities now.")

    def cmd_save(self, args: list[str]):
        if not args:
            print("Usage: save <name>")
            return

        name = args[0]
        out_dir = Path("blueprints/handcrafted")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / f"{name}.json"

        data = {
            "label": self.label,
            "description": self.description,
            "tags": self.tags,
            "favorites": 0,
            "source": "handcrafted",
            "entity_count": len(self.entities),
            "entities": [
                {"name": e.name, "x": e.x, "y": e.y, "direction": e.direction}
                for e in self.entities
            ],
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"  Saved to {path} ({len(self.entities)} entities)")

    def cmd_load(self, args: list[str]):
        if not args:
            print("Usage: load <path>")
            return

        path = Path(args[0])
        if not path.exists():
            print(f"  File not found: {path}")
            return

        with open(path) as f:
            data = json.load(f)

        # Handle list (crawled format) or dict (handcrafted format)
        if isinstance(data, list):
            data = data[0]

        self._save_undo()
        self.entities = [
            EntitySpec(name=e["name"], x=e["x"], y=e["y"], direction=e.get("direction", 0))
            for e in data.get("entities", [])
        ]
        self.label = data.get("label", "")
        self.description = data.get("description", "")
        self.tags = data.get("tags", [])
        print(f"  Loaded '{self.label}' — {len(self.entities)} entities")

    def cmd_paste(self, args: list[str]):
        """Paste a Factorio blueprint string (starts with '0')."""
        if not args:
            print("Usage: paste <blueprint_string>")
            print("  Copy a blueprint in Factorio, then: paste 0eNp...")
            return

        bp_string = args[0]
        if not bp_string.startswith("0"):
            print("  Blueprint strings start with '0'. Got: " + bp_string[:20])
            return

        from fle.grid_codec.blueprint import from_blueprint_string
        try:
            bp = from_blueprint_string(bp_string, label=self.label, description=self.description)
        except Exception as e:
            print(f"  Failed to decode: {e}")
            return

        if not bp.entities:
            # Might be a blueprint book — try that
            from fle.grid_codec.blueprint import decode_blueprint_book, raw_entities_to_specs
            try:
                decoded = decode_blueprint_book(bp_string)
                if decoded:
                    print(f"  Blueprint book with {len(decoded)} blueprints:")
                    for i, (meta, raw_ents) in enumerate(decoded):
                        specs = raw_entities_to_specs(raw_ents)
                        label = meta.get("label", "unlabeled")
                        print(f"    [{i}] \"{label}\" — {len(specs)} entities")
                    choice = input("  Which one? (number): ").strip()
                    try:
                        idx = int(choice)
                        meta, raw_ents = decoded[idx]
                        self._save_undo()
                        self.entities = raw_entities_to_specs(raw_ents)
                        self.label = meta.get("label", self.label)
                        self.description = meta.get("description", self.description)
                        print(f"  Loaded '{self.label}' — {len(self.entities)} entities")
                        return
                    except (ValueError, IndexError):
                        print("  Invalid choice.")
                        return
            except Exception as e:
                print(f"  Failed to decode as book: {e}")
                return

        self._save_undo()
        self.entities = bp.entities
        if bp.label:
            self.label = bp.label
        print(f"  Pasted '{self.label}' — {len(self.entities)} entities")

        # Normalize positions so top-left is near (0,0)
        if self.entities:
            min_x = min(e.x for e in self.entities)
            min_y = min(e.y for e in self.entities)
            for e in self.entities:
                e.x -= min_x
                e.y -= min_y
            print(f"  Positions normalized (shifted by {-min_x},{-min_y})")

    def cmd_entities(self, args: list[str]):
        filt = args[0].lower() if args else ""
        matches = [info for info in ENTITY_REGISTRY.all_entities() if filt in info.name]
        for info in matches:
            print(f"  {info.name:35s} {info.width}x{info.height}  ({info.category})")
        print(f"  ({len(matches)} entities)")

    def cmd_label(self, args: list[str]):
        self.label = " ".join(args)
        print(f"  Label: {self.label}")

    def cmd_desc(self, args: list[str]):
        self.description = " ".join(args)
        print(f"  Description: {self.description}")

    def cmd_tags(self, args: list[str]):
        self.tags = args
        print(f"  Tags: {self.tags}")

    def cmd_help(self, _args: list[str]):
        print(__doc__)

    def run(self):
        commands = {
            "place": self.cmd_place,
            "p": self.cmd_place,
            "remove": self.cmd_remove,
            "rm": self.cmd_remove,
            "list": self.cmd_list,
            "ls": self.cmd_list,
            "show": self.cmd_show,
            "s": self.cmd_show,
            "clear": self.cmd_clear,
            "undo": self.cmd_undo,
            "u": self.cmd_undo,
            "save": self.cmd_save,
            "load": self.cmd_load,
            "paste": self.cmd_paste,
            "v": self.cmd_paste,
            "entities": self.cmd_entities,
            "e": self.cmd_entities,
            "label": self.cmd_label,
            "desc": self.cmd_desc,
            "tags": self.cmd_tags,
            "help": self.cmd_help,
            "h": self.cmd_help,
            "?": self.cmd_help,
        }

        print("Blueprint Editor — type 'help' for commands")
        print(f"  {len(ENTITY_REGISTRY.names())} entity types available\n")

        while True:
            try:
                line = input("bp> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nBye.")
                break

            if not line:
                continue

            parts = line.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ("quit", "q", "exit"):
                print("Bye.")
                break

            if cmd in commands:
                commands[cmd](args)
            else:
                print(f"  Unknown command '{cmd}'. Type 'help' for commands.")


def main():
    editor = BlueprintEditor()
    editor.run()


if __name__ == "__main__":
    main()
