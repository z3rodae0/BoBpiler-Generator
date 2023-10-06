import json
import generator_utils as g
import subprocess
import uuid
import os
import random
import queue

def run_csmith(code_gen_queue, csmith_path, yarpgen_path):
    #csmith과 관련된 작업들을 실행하는 함수
    command_csmith = [csmith_executable] + csmith_options
    p_csmtih = subprocess.Popen(command_csmith, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    g.generator_handshake(p_csmtih)
    g.generator_clinet(p_csmtih, "csmith", code_gen_queue, csmith_path, yarpgen_path)

def csmith_todo(p, code_gen_queue, csmith_path):
    #tmp 디렉토리 생성 및 csmith or yarpgen forkserver와 통신(파일명|시드값 전달)
    _uuid = str(uuid.uuid4())
    dir_path = csmith_path + _uuid
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file_path = dir_path + '/'  + _uuid + '.c'
    
    seed = random.randint(1, 4294967296)
    input_seed = file_path + "|" + str(seed)
    p.stdin.write(input_seed + '\n')
    p.stdin.flush()

    json_csmith = p.stdout.readline()
    process_json(json_csmith, code_gen_queue, file_path, _uuid)

def process_json(json_csmith, code_gen_queue, file_path, _uuid):
    #csmith or yarpgen에서 받은 JSON 데이터 출력 및 처리
    try:
        result = json.loads(json_csmith)
        generator_name = result["generator"]
        return_code = result["return_code"]

        print(f"[+] Generator: {generator_name}")
        print(f"    Return Code: {return_code}")

        json_csmith = csmith_json(file_path, _uuid)
        code_gen_queue.put(json.loads(json_csmith))
    except json.JSONDecodeError:
        print("[!] JSON 데이터를 파싱하는데 문제가 발생했습니다.")

def csmith_json(file ,_uuid):
    #컴파일 시스템에서 사용하는 JSON 인터페이스 생성 및 출력
    data = {
        "generator" : 'csmith',
        "uuid" : _uuid,
        "file_path" : file
    }
    json_str = json.dumps(data)
    print(json_str)
    return json_str

csmith_options = [
    '--max-array-dim', '3', 
    '--max-array-len-per-dim', '10', 
    '--max-block-depth', '3', 
    '--max-block-size', '5', 
    '--max-expr-complexity', '10', 
    '--max-funcs', '3', 
    '--max-pointer-depth', '3', 
    '--max-struct-fields', '10', 
    '--max-union-fields', '10', 
    '--muls', '--safe-math', 
    '--no-packed-struct', 
    '--paranoid', 
    '--pointers', 
    '--structs', 
    '--unions', 
    '--volatiles', 
    '--volatile-pointers', 
    '--const-pointers', 
    '--global-variables', 
    '--no-builtins', 
    '--inline-function', 
    '--inline-function-prob', '50'
]

csmith_executable = "csmith_forkserver" #csmith_forkserver 바이너리
