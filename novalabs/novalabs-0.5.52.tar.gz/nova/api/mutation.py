from gql import gql


class GraphMutation:
    
    @staticmethod
    def create_pair():
        return gql(
            """
            mutation createPair($input: PairInput!){
                createPair(input: $input) {
                    _id
                    name
                }
            }
            """
        )

    @staticmethod
    def delete_pair():
        return gql(
            """
            mutation deletePair($pairId: ObjectId!){
                deletePair(pairId: $pairId)
                
            }
            """
        )

    @staticmethod
    def update_pair():
        pass

    @staticmethod
    def create_strategy_query():
        return gql(
        """
            mutation createStrategy($input: StrategyInput!){
                createStrategy(input: $input) {
                    _id
                    name
                    candles
                    avg_expd_return
                    avg_reel_return
                }
            }
        """)
    
    @staticmethod
    def create_bot_query():
        return gql(
        """
            mutation createBot($input: BotInput!) {
                createBot(input: $input) {
                    name
                    exchange
                    strategy {
                        name
                        candles
                    }
                }
            }
        """)

    @staticmethod
    def new_bot_position_query():
        return gql(
            """
            mutation newBotPosition($name: String!, $input: PositionInput!) {
                newBotPosition(name: $name, input: $input) {
                    _id
                }
            }
            """)
        
    @staticmethod
    def update_bot_position_query():
        return gql(
            """
            mutation editPosition($input: PositionInput!){
                editPosition(input: $input){
                    _id
                    state
                }
            }
            """)

    @staticmethod
    def delete_position():
        return gql(
            """
            mutation deletePosition($positionId: ObjectId!){
                deletePosition(positionId: $positionId)

            }
            """
        )
