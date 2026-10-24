"""The `fle` CLI only runs game servers and fetches render sprites."""

import pytest

from fle.run import build_parser, main


def _subcommands() -> set[str]:
    parser = build_parser()
    action = next(a for a in parser._actions if a.dest == "command")
    return set(action.choices)


def test_only_game_interface_commands():
    assert _subcommands() == {"cluster", "sprites"}


def test_cluster_arguments():
    args = build_parser().parse_args(["cluster", "start", "-n", "2", "-s", "open_world"])
    assert (args.command, args.cluster_command, args.n, args.s) == ("cluster", "start", 2, "open_world")


def test_sprites_defaults():
    args = build_parser().parse_args(["sprites"])
    assert args.spritemap_dir == ".fle/spritemaps"
    assert args.sprite_dir == ".fle/sprites"
    assert args.force is False


def test_harness_commands_are_rejected():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["inspect-eval"])


def test_no_command_prints_help_and_exits(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["fle"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    assert "cluster" in capsys.readouterr().out
