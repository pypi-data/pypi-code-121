"""! @brief Pipeline test entry point."""
from pipeline.pipeline import generatedProjectNamePipeline


##
# @file
#
# @brief Pipeline test entry point.
if __name__ == '__main__':
    ## Creates an instance of the pipeline
    p = generatedProjectNamePipeline()

    ## This method executes the pipeline, dataset and required params can be loaded here.\n
    # Examples:
    # @code
    # data = {}
    # for file in data_files:
    #     with open(file) as f:
    #         data = load_json(f)
    #
    # output = p.execute(**data)
    # @endcode
    # or
    # @code
    # p.execute(data=mydata)
    # @endcode
    # or
    # @code
    # sig = Signature(uid=1, text=signature, hints=None)
    # output = p.execute(signatures=[sig])
    # @endcode
    # Define data passed through the execute method in the schema/<my-new-project>Inputs.py class, for example:
    # @code
    # class <my-new-project>Inputs(BaseModel):
    #     signatures: List[Signature]
    # @endcode
    # or
    # @code
    # class <my-new-project>Inputs(BaseModel):
    #     data = {}
    # @endcode

    output = p.execute()
    print(output)
