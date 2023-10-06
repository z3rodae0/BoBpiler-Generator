import multiprocessing
import csmith_utils as c
import yarpgen_utils as y
import queue

def gen_main(csmith_path, yarpgen_path):
    #생성할 디렉토리 위치 인자로 넘겨주면 됨
    global code_gen_queue
    code_gen_queue = multiprocessing.Queue(maxsize=1000)

    csmith_process = multiprocessing.Process(target=c.run_csmith, args=(code_gen_queue, csmith_path, yarpgen_path))
    yarpgen_process = multiprocessing.Process(target=y.run_yarpgen, args=(code_gen_queue, csmith_path, yarpgen_path))

    csmith_process.start()
    yarpgen_process.start()

    csmith_process.join()
    yarpgen_process.join()
