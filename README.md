# AlphaRegexPublic

## AlphaRegex : Synthesizer for regular expressions
AlphaRegex is a synthesizer that instantly outputs regular expressions from examples for introductory automata classes.
This work was conducted under the guidance of Prof.Hakjoo Oh (http://prl.korea.ac.kr) in Korea University.

## Paper
AlphaRegex performs over- and under-approximations of partial regular expressions to accelerate the speed.
For the more details, please refer to our GPCE '16 paper ["Synthesizing Regular Expressions from Examples for Introductory Automata Assignments"](https://dl.acm.org/doi/10.1145/2993236.2993244).
Please cite our paper if you find our work is intriguing.

## How to build
### Install and Initialize Dependencies
- `sudo apt install opam time`
- `opam init -y`
- `echo -e "\n\ntest -r ~/.opam/opam-init/init.sh && . ~/.opam/opam-init/init.sh > /dev/null 2> /dev/null || true" >> ~/.profile`
- `eval $(opam env --switch=default)`
- `opam install batteries camlp-streams dune num ocamlbuild ocamlfind`

### Build
After you clone this project, follow the steps below (on Ubuntu).
- `dune build`

## How to use
To use AlphaRegex, you need to provide:
- Positive examples
- Negative examples

```
dune exec ./main.exe -- -input <filename>
```

Then, AlphaRegex quickly derives a regular expression that accepts all the positive examples and rejects all the negative examples.
For example, run `dune exec ./main.exe -- -input ../benchmarks/no1_start_with_0`, then AlphaRegex should generate the solution `0(0+1)*`.
In the `benchmarks` directory, there are benchmark examples that we used for evaluation and you can easily check how positive/negative examples should be given to AlphaRegex.

## Contact
AlphaRegex is maintained by [Programming Research Laboratory in Korea University](http://prl.korea.ac.kr).
If you have any questions, feel free to email us: hakjoo\_oh@korea.ac.kr, sunbeom\_so@korea.ac.kr
