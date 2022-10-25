# pyratings - Working with credit ratings, professionally and efficiently

**Documentation**: [https://hsbc.github.io/pyratings/](https://hsbc.github.io/pyratings/)

**Source Code**: [https://github.com/hsbc/pyratings/](https://github.com/hsbc/pyratings/)

---

This library consists of functions, which will be helpful in order to work with 
credit ratings.

_pyratings_ offers the following capabilities:

* Cleaning ratings for further processing, e.g. stripping off of rating watches.
* Transform long- and short-term ratings into rating scores and vice versa.
* Compute best/second best/worst ratings on a security level basis within a
  portfolio context.
* Compute average ratings/rating scores on a portfolio level.
* Compute Weighted Average Rating Factor (WARF) on a portfolio level.
* Compute WARF buffer, i.e. distance from current WARF to next maxWARF.

Transformations from ratings to scores/WARF and vice versa will take place according 
to the following translation table:

| Moody’s |  S&P | Fitch |  ICE | DBRS | Bloomberg | Score |  WARF | MinWARF* | MaxWARF* |
|:-------:|:----:|:-----:|:----:|:----:|:---------:|------:|------:|---------:|---------:|
|   Aaa   |  AAA |  AAA  |  AAA |  AAA |    AAA    |     1 |     1 |        1 |        5 |
|   Aa1   |  AA+ |  AA+  |  AA+ |  AAH |    AA+    |     2 |    10 |        5 |       15 |
|   Aa2   |  AA  |   AA  |  AA  |  AA  |    AA     |     3 |    20 |       15 |       30 |
|   Aa3   |  AA- |  AA-  |  AA- |  AAL |    AA-    |     4 |    40 |       30 |       55 |
|    A1   |  A+  |   A+  |  A+  |  AH  |    A+     |     5 |    70 |       55 |       95 |
|    A2   |   A  |   A   |   A  |   A  |     A     |     6 |   120 |       95 |      150 |
|    A3   |  A-  |   A-  |  A-  |  AL  |    A-     |     7 |   180 |      150 |      220 |
|   Baa1  | BBB+ |  BBB+ | BBB+ | BBBH |   BBB+    |     8 |   260 |      220 |      310 |
|   Baa2  |  BBB |  BBB  |  BBB |  BBB |    BBB    |     9 |   360 |      310 |      485 |
|   Baa3  | BBB- |  BBB- | BBB- | BBBL |   BBB-    |    10 |   610 |      485 |      775 |
|   Ba1   |  BB+ |  BB+  |  BB+ |  BBH |    BB+    |    11 |   940 |      775 |     1145 |
|   Ba2   |  BB  |   BB  |  BB  |  BB  |    BB     |    12 |  1350 |     1145 |     1558 |
|   Ba3   |  BB- |  BB-  |  BB- |  BBL |    BB-    |    13 |  1766 |     1558 |     1993 |
|    B1   |  B+  |   B+  |  B+  |  BH  |    B+     |    14 |  2220 |     1993 |     2470 |
|    B2   |   B  |   B   |   B  |   B  |     B     |    15 |  2720 |     2470 |     3105 |
|    B3   |  B-  |   B-  |  B-  |  BL  |    B-     |    16 |  3490 |     3105 |     4130 |
|   Caa1  | CCC+ |  CCC+ | CCC+ | CCCH |   CCC+    |    17 |  4770 |     4130 |     5635 |
|   Caa2  |  CCC |  CCC  |  CCC |  CCC |    CCC    |    18 |  6500 |     5635 |     7285 |
|   Caa3  | CCC- |  CCC- | CCC- | CCCL |   CCC-    |    19 |  8070 |     7285 |     9034 |
|    Ca   |  CC  |   CC  |  CC  |  CC  |    CC     |    20 |  9998 |     9034 |   9998.5 |
|    C    |   C  |   C   |   C  |   C  |     C     |    21 |  9999 |   9998.5 |   9999.5 |
|    D    |   D  |   D   |   D  |   D  |    DDD    |    22 | 10000 |   9999.5 |    10000 |

`MinWARF` is inclusive, while `MaxWARF` is exclusive.

Short-term ratings

| Moody’s | S&P  | Fitch |    DBRS    | Score |
|:-------:|:----:|:-----:|:----------:| -----:|
|   P-1   | A-1+ |  F1+  | R-1 (high) |     1 |
|         |      |       | R-1 (mid)  |     2 |
|         |      |       | R-1 (low)  |     3 |
|         | A-1  |  F1   | R-2 (high) |     5 |
|         |      |       | R-2 (mid)  |     6 |
|   P-2   | A-2  |  F2   | R-2 (low)  |     7 |
|         |      |       | R-3 (high) |     8 |
|   P-3   | A-3  |  F3   | R-3 (mid)  |     9 |
|         |      |       | R-3 (low)  |    10 |
|   NP    |  B   |       |    R-4     |    12 |
|         |      |       |    R-5     |    15 |
|         |  C   |       |            |    18 |
|         |  D   |       |     D      |    22 |
