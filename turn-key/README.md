# magpieCTF 2022 - Turn Key Writeup

By: Nectarios Chroniaris

## Compiled PDF

There is an [already compiled version of the report](./turn-key.pdf), included alongside the source files.

## Building From Sources

This report is built with LaTeX, so most TeX distribution should work. I used MiKTeX, for the record. To compile, run the following:

```shell
cd turn-key/src/
pdflatex -file-line-error -interaction=nonstopmode -synctex=1 -output-format=pdf -output-directory=../out -aux-directory=../auxil ./turn-key.tex
```
