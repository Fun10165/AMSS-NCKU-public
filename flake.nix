{
  description = "AMSS-NCKU reproducible dev/test shell (Ubuntu 22.04 compatible toolchain profile)";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";

  outputs = { self, nixpkgs }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = with pkgs; [
          gcc
          gfortran
          openmpi
          gnumake
          cmake
          pkg-config
          rustc
          cargo
          rustfmt
          clippy
          rust-analyzer
          python3
          python3Packages.pytest
          python3Packages.pytest-cov
          python3Packages.numpy
          python3Packages.scipy
          python3Packages.matplotlib
          python3Packages.sympy
        ];

        shellHook = ''
          export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
          export OMPI_MCA_rmaps_base_oversubscribe=1
          echo "Entered Nix dev shell (nixos-22.11 profile)."
          echo "Run Python tests:  python -m pytest"
          echo "Run native tests:  ./scripts/test_native.sh"
          echo "Rust toolchain:   cargo --version && rustc --version"
        '';
      };
    };
}
