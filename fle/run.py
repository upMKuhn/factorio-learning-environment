import argparse
import subprocess
import sys
from pathlib import Path


def fle_cluster(args):
    cluster_path = Path(__file__).parent / "cluster"
    script = cluster_path / "run-envs.sh"
    if not script.exists():
        print(f"Cluster script not found: {script}", file=sys.stderr)
        sys.exit(1)
    cmd = [str(script)]
    if args:
        if args.cluster_command:
            cmd.append(args.cluster_command)
        if args.n:
            cmd.extend(["-n", str(args.n)])
        if args.s:
            cmd.extend(["-s", args.s])
    try:
        subprocess.run(cmd, cwd=str(cluster_path), check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running cluster script: {e}", file=sys.stderr)
        sys.exit(e.returncode)


def fle_sprites(args):
    # Imported lazily: huggingface_hub is only needed for this command.
    from fle.env.tools.admin.render.sprites.download import (
        download_sprites_from_hf,
        generate_sprites,
    )

    try:
        # Download spritemaps from HuggingFace
        print("Downloading spritemaps...")
        success = download_sprites_from_hf(
            output_dir=args.spritemap_dir, force=args.force, num_workers=args.workers
        )

        if not success:
            print("Failed to download spritemaps", file=sys.stderr)
            sys.exit(1)

        # Generate individual sprites from spritemaps
        print("\nGenerating sprites...")
        success = generate_sprites(
            input_dir=args.spritemap_dir, output_dir=args.sprite_dir
        )

        if not success:
            print("Failed to generate sprites", file=sys.stderr)
            sys.exit(1)

        print("\nSprites successfully downloaded and generated!")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fle",
        description="Factorio Learning Environment CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fle cluster [start|stop|restart|help] [-n N] [-s SCENARIO]
  fle sprites [--force] [--workers N]
        """,
    )
    subparsers = parser.add_subparsers(dest="command")
    parser_cluster = subparsers.add_parser(
        "cluster", help="Setup Docker containers (run run-envs.sh)"
    )
    parser_cluster.add_argument(
        "cluster_command",
        nargs="?",
        choices=["start", "stop", "restart", "help"],
        help="Cluster command (start/stop/restart/help)",
    )
    parser_cluster.add_argument("-n", type=int, help="Number of Factorio instances")
    parser_cluster.add_argument(
        "-s",
        type=str,
        help="Scenario (open_world or default_lab_scenario)",
    )

    parser_sprites = subparsers.add_parser(
        "sprites", help="Download and generate sprites for the render tool"
    )
    parser_sprites.add_argument(
        "--force", action="store_true", help="Force re-download even if sprites exist"
    )
    parser_sprites.add_argument(
        "--workers",
        type=int,
        default=10,
        help="Number of parallel download workers (default: 10)",
    )
    parser_sprites.add_argument(
        "--spritemap-dir",
        type=str,
        default=".fle/spritemaps",
        help="Directory to save downloaded spritemaps (default: .fle/spritemaps)",
    )
    parser_sprites.add_argument(
        "--sprite-dir",
        type=str,
        default=".fle/sprites",
        help="Directory to save generated sprites (default: .fle/sprites)",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "cluster":
        fle_cluster(args)
    elif args.command == "sprites":
        fle_sprites(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
