{
  description = "korg flake";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, ... }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pkgs-spin = import (builtins.fetchTarball {
          url = "https://github.com/NixOS/nixpkgs/archive/893c51bda8b7502b43842f137258d0128097d7ea.tar.gz";
          sha256 = "0wydvj05k9cjx557gvr1am7rzl482zv9ml0p3zamxm1gx7whzja6";
        }) { inherit system; }; 

        spinPkg = pkgs-spin.spin;

      in
      {
        packages.default = pkgs.stdenv.mkDerivation {
          pname = "korg";
          src = self;
          installPhase = ''
            mkdir -p $out/bin
            echo "placeholder" > $out/bin/korg
          '';
        };

        devShells.default = pkgs.mkShellNoCC rec {
          buildInputs = [
            pkgs.python3  
            spinPkg      
            pkgs.python313Packages.pyyaml
          ];

          shellHook = ''
            echo "Switching to korg dev-shell... :D"
          '';
        };
      }
    );
}
