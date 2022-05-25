"""!
@mainpage Documentation

@section general_main General:
The dsframework was developed to unify and simplify our work by creating a structured work methodology. It allows you
to generate your own project out of a template which includes a default pipeline with the most common steps for
a data scientist to use.
The framework supports two project types (Streaming / Batch). Files will be created for both. Please refer to the
appropriate quickstart pages for more details

@section benefits Benefits:
- Connection to ds-portal.
- Ready testing environment: local testing and cloud evaluation.
- Hide a lot of boilerplate code
- Abstract access to multiple services (AWS, GCP products, Docker, DVC, etc.)
- Generate a pipeline with predefined four steps (that can be extended), it gives the flexibility for
a data scientist developer to load data, pass it through preprocessing procedures, a model, forcer and
run post process procedures.

@section notes_main Steps
The main default four steps included are:
- Preprocess
- Predictor
- Forcer
- Postprocessor

@section usg_main Start here:
For more information about:
 1. [Installing the ds-framework and generating a new project](QUICKSTART1.md) (@subpage quick_start1).
 2. [Setting up the project](QUICKSTART2.md) (@subpage quick_start2).
 3. [Test your project](QUICKSTART3.md) (@subpage quick_start3).
 4. [Set up a batch project](QUICKSTART4.md) (@subpage quick_start4).
 5. [Additional cli commands, server endpoints and ignore files](MOREINFO.md) (@subpage more_info).


**Version** 1.1

Copyright (c) 2022 ZoomInfo.  All rights reserved.
"""