{
  description = "A collection of general-purpose VapourSynth functions to be reused in modules and scripts.";

  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }: flake-utils.lib.eachDefaultSystem (system: 
    let
      pkgs = import nixpkgs {
        inherit system;
      };

      ## Change this to update python versions.
      ## run "nix flake lock --update-input nixpkgs" after you did that.
      python = pkgs.python310;

      # Fix brokenness of nix-VapourSynth on darwin
      vapoursynth = pkgs.vapoursynth.overrideAttrs (old: {
        patches = [];
        meta.broken = false;
        meta.platforms = [ system ];
      });

      # The python package for the python version of choice.
      vapoursynth_python = python.pkgs.buildPythonPackage {
        pname = "vapoursynth";
        inherit (pkgs.vapoursynth) version src;
        nativeBuildInputs = [ 
          python.pkgs.cython 
        ];
        buildInputs = [
          vapoursynth
        ];
      };
    in
    {
      devShells.default = pkgs.mkShell {
        buildInputs = [
          (python.withPackages (ps: [
            vapoursynth_python
          ]))
        ];
      };
      devShell = self.devShell.${system}.default;

      packages.default = python.pkgs.buildPythonPackage {
        pname = "vsutil";
        version = "0.7.0";
        src = ./.;
        buildInputs = [
          vapoursynth_python 
        ];
        checkPhase = ''
          ${python}/bin/python -m unittest discover -s $src/tests
        '';
      };
      defaultPackage = self.packages.${system}.default;
    }
  );
}
