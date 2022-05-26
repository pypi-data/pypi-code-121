def get_position(conn, query):
    data = conn.get_data(query=query)[0]
    if data:
        return data[0][0].replace("[", '').replace("]", '').replace("'", '')
    return 'Not found data.'