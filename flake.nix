{
  inputs = {
        nixpkgs.url = "nixpkgs/nixos-23.11";
    };

  outputs = { self, nixpkgs }:
    let
        system = "x86_64-linux";
        pkgs = nixpkgs.legacyPackages.${system};
        deps = with pkgs; [
            python3
            python3Packages.xlib
            python3Packages.setuptools
            python3Packages.tkinter
            python3Packages.pynvim
            usbutils
            neovim-qt
            git
        ];
    in {
        packages.${system} = rec {
            client = pkgs.stdenv.mkDerivation {
                name = "ht3-client";
                buildInputs = [ pkgs.python3 ];
                dontUnpack = true;
                installPhase = ''
                    mkdir -p $out/bin
                    echo "PYTHONPATH='$PYTHONPATH:${self}' python -m client" > $out/bin/ht3-client
                    chmod +x $out/bin/ht3-client
                '';
            };
            default = pkgs.stdenv.mkDerivation {
                name = "ht3";
                buildInputs = deps;
                dontUnpack = true;
                installPhase = ''
                    mkdir -p $out/bin
                    echo "PYTHONPATH='$PYTHONPATH:${self}' python -m ht3" > $out/bin/ht3
                    chmod +x $out/bin/ht3
                '';
            };
        };


        devShells.${system}.default = pkgs.mkShell {
            buildInputs = deps;
            shellHook = ''
                PYTHONPATH="$PYTHONPATH:${self}"
                echo 'HT3 Dev Shell ${self} '
            '';
        };
   };
}
