from re import template
from textwrap import dedent


def load_templates():
    specialization = input("Name of the specialization: ")
    course = input("Number of the course: ")
    week = input("Number of the week: ")
    version = input("Version of the grader (leave empty for version 1): ")
    version = 1 if not version else version

    dockerfile = """
	FROM frolvlad/alpine-miniconda3:python3.7

	RUN apk update && apk add libstdc++

	COPY requirements.txt .

	RUN pip install -r requirements.txt && \
	rm requirements.txt

	RUN mkdir /grader && \ 
	mkdir /grader/submission

	COPY .conf /grader/.conf
	COPY data/ /grader/data/
	COPY solution/ /grader/solution/
	COPY entry.py /grader/entry.py
	COPY grader.py /grader/grader.py

	RUN chmod a+rwx /grader/

	WORKDIR /grader/

	ENTRYPOINT ["python", "entry.py"]
    """

    conf = f"""
	ASSIGNMENT_NAME=C{course}W{week}_Assignment
	IMAGE_NAME={specialization}c{course}w{week}-grader
	GRADER_VERSION={version}
	TAG_ID=V$(GRADER_VERSION)
	SUB_DIR=mount
	MEMORY_LIMIT=4096
	LINUX_UPLOAD_DIR='/mnt/c/Users/Andres/dlai/upload'
	MAC_UPLOAD_DIR='/Users/andreszarta/Desktop/upload-temp'
    """

    makefile = """
	include .conf

	PARTIDS = ""
	OS := $(shell uname)

	learner:
		[ "$(ls -A ./$(SUB_DIR))" ] && rm ./$(SUB_DIR)/* && echo "Deleted previous version"|| echo "Empty"
		cp mount/submission.ipynb learner/$(ASSIGNMENT_NAME)_Solution.ipynb
		learner -fn learner/$(ASSIGNMENT_NAME)_Solution.ipynb 
		rm learner/$(ASSIGNMENT_NAME)_Solution.ipynb && rm learner/$(ASSIGNMENT_NAME)_Solution.py && rm learner/$(ASSIGNMENT_NAME).py

	build:
		docker build -t $(IMAGE_NAME):$(TAG_ID) .

	entry:
		docker run -it --rm --mount type=bind,source=$(PWD)/mount,target=/shared/submission --mount type=bind,source=$(PWD),target=/grader/ --entrypoint ash $(IMAGE_NAME):$(TAG_ID)

	test:
		docker run -it --rm --mount type=bind,source=$(PWD)/mount,target=/shared/submission --mount type=bind,source=$(PWD),target=/grader/ --entrypoint pytest $(IMAGE_NAME):$(TAG_ID)

	grade:
		gradethis $(PARTIDS) $(IMAGE_NAME):$(TAG_ID) $(SUB_DIR) $(MEMORY_LIMIT)

	mem:
		memthis $(PARTIDS)

	zip:
		zip -r $(IMAGE_NAME)$(TAG_ID).zip .

	clean:
		find . -maxdepth 1 -type f -name "*.zip" -exec rm {} +
		docker rm $$(docker ps -qa --no-trunc --filter "status=exited")
		docker rmi $$(docker images --filter "dangling=true" -q --no-trunc)

	upload:
		coursera_autograder --timeout 1800 upload --grader-memory-limit $(MEMORY_LIMIT) --grading-timeout 1800 $(IMAGE_NAME)$(TAG_ID).zip $(COURSE_ID) $(ITEM_ID) $(PART_ID)

	move-zip:
		if [[ "$(OS)" == "Darwin" ]];    \
		then    \
			mv $(IMAGE_NAME)$(TAG_ID).zip $(MAC_UPLOAD_DIR);    \
		else    \
			mv $(IMAGE_NAME)$(TAG_ID).zip $(LINUX_UPLOAD_DIR);    \
		fi

	move-learner:
		if [[ "$(OS)" == "Darwin" ]];    \
		then    \
			cp learner/$(ASSIGNMENT_NAME).ipynb $(MAC_UPLOAD_DIR);    \
		else    \
			cp learner/$(ASSIGNMENT_NAME).ipynb $(LINUX_UPLOAD_DIR);    \
		fi
    """


    grader_py = """
	from types import ModuleType, FunctionType, FunctionType
	from typing import Dict, List, Optional
	from dlai_grader.grading import test_case, object_to_grade
	from dlai_grader.types import grading_function, grading_wrapper


	def part_1(
		learner_mod: ModuleType, solution_mod: Optional[ModuleType]
	) -> grading_function:
		@object_to_grade(learner_mod, "learner_func")
		def g(learner_func: FunctionType) -> List[test_case]:

			t = test_case()
			if not isinstance(learner_func, FunctionType):
				t.failed = True
				t.msg = "learner_func has incorrect type"
				t.want = FunctionType
				t.got = type(learner_func)
				return [t]

			cases: List[test_case] = []

			return cases

		return g


	def handle_part_id(part_id: str) -> grading_wrapper:
		grader_dict: Dict[str, grading_wrapper] = {
			"": part_1,
		}
		return grader_dict[part_id]
	"""


    template_dict = {
		"dockerfile": dedent(dockerfile[1:]),
		"makefile": dedent(makefile[1:]),
		"conf": dedent(conf[1:]),
		"grader_py": dedent(grader_py[1:])
	}

    return template_dict

