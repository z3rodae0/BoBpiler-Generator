import ctypes

# 라이브러리 로드
csmith_function = ctypes.WinDLL('.\\csmith.dll')

# 함수 프로토타입 정의
csmith_function.gen_csmith.argtypes = (ctypes.c_int, ctypes.POINTER(ctypes.c_char_p))

def make_param(str_list):
    c_string_array = (ctypes.c_char_p * len(str_list))()
    for i, string in enumerate(str_list):
        c_string_array[i] = bytes(string, 'utf-8')
    return len(str_list), c_string_array

# 테스트
if __name__ == "__main__":
    test_strings = ["csmith", "--max-array-dim","3", "-o", "32132.c"]
    ret = csmith_function.gen_csmith(*make_param(test_strings))
    print(ret)