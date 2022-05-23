from pollination_streamlit.authentication import _decrypt_cookie


def test_decrypt():
    cookie = "MTY0NzUyMTM2M3xjM1Z3WlhJdGMyVmpjbVYwTFhaaGJIVmx8Zq5Ks3q90QdgL5znATZfz5LsGWUcSc5CGIOeZn-EQBE="
    value = "super-secret-value"
    assert _decrypt_cookie(cookie) == value
