let
  pkgs = import <nixpkgs> {};
in pkgs.mkShell {
  packages = [
    (pkgs.python3.withPackages (python-pkgs: [
      python-pkgs.flake8
      python-pkgs.black
      python-pkgs.isort
      python-pkgs.pytest
    ]))
  ];
  shellHook =
  ''
    echo HT3 Dev Shell
  '';
}
