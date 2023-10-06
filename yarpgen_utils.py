import json
import generator_utils as g
import subprocess
import uuid
import os
import random
import queue

def run_yarpgen(code_gen_queue, csmith_path, yarpgen_path):
    #yarpgen과 관련된 작업들을 실행하는 함수
    command_yargpen = [yarpgen_executable] + yarpgen_options
    p_yarpgen = subprocess.Popen(command_yargpen, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    g.generator_handshake(p_yarpgen)
    g.generator_clinet(p_yarpgen, "yarpgen", code_gen_queue, csmith_path, yarpgen_path)

def yarpgen_todo(p, code_gen_queue, yarpgen_path):
    #tmp 디렉토리 생성 및 csmith or yarpgen forkserver와 통신(파일명|시드값 전달)
    _uuid = str(uuid.uuid4())
    dir_path = yarpgen_path + _uuid
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    seed = random.randint(1, 4294967296)
    mutation_seed = random.randint(1, 4294967296)

    input_seed = dir_path + "|" + str(seed) + "|" + str(mutation_seed)
    p.stdin.write(input_seed + '\n')
    p.stdin.flush()

    p.stdout.readline() 
    p.stdout.readline() 
    json_yarpgen = p.stdout.readline()
    process_json(json_yarpgen, code_gen_queue, dir_path, _uuid)

def process_json(json_yarpgen, code_gen_queue, dir_path, _uuid):
    #csmith or yarpgen에서 받은 JSON 데이터 출력 및 처리
    try:
        result = json.loads(json_yarpgen)
        generator_name = result["generator"]
        return_code = result["return_code"]

        print(f"[+] Generator: {generator_name}")
        print(f"    Return Code: {return_code}")

        json_yarpgen = yarpgen_json(dir_path, _uuid)
        code_gen_queue.put(json.loads(json_yarpgen))
    except json.JSONDecodeError:
        print("[!] JSON 데이터를 파싱하는데 문제가 발생했습니다.")

def yarpgen_json(file, _uuid):
    #컴파일 시스템에서 사용하는 JSON 인터페이스 생성 및 출력
    file = file + "/func.c" + "|" + file + "/driver.c"
    data = {
        "generator" : 'yarpgen',
        "uuid" : _uuid,
        "file_path": file
    }
    json_str = json.dumps(data)
    print(json_str)
    return json_str

yarpgen_options = ["--std=c", "--mutate=all"]

yarpgen_executable = "yarpgen_forkserver" #yarpgen_forkserver 바이너리
