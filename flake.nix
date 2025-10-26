{
  description = "korg flake";

  inputs = {
    nixpkgs.url     = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs-spin.url = "github:NixOS/nixpkgs/893c51bda8b7502b43842f137258d0128097d7ea";
  };

  outputs = { self, nixpkgs, flake-utils, nixpkgs-spin, ... } @ inputs:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pkgs-spin = nixpkgs-spin.legacyPackages.${system};
      in {
        packages.default = pkgs.stdenv.mkDerivation {
          pname   = "korg";
          src     = ./.;
        };

        devShells.default = pkgs.mkShellNoCC rec {
          buildInputs = with pkgs; [
            # spin
            python3
          ] ++ [
            pkgs-spin.spin
          ];

          shellHook = ''
            echo "Switching to korg dev-shell... :D"
          '';
        };
      }
    );
}
