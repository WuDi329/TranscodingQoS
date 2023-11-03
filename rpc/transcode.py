import asyncio

import grpc

import transcoding_pb2
import transcoding_pb2_grpc

from loguru import logger

# 临时队列
queue_list = []

# Coroutines to be invoked when the event loop is shutting down.
_cleanup_coroutines = []


class Transcoder(transcoding_pb2_grpc.TranscoderServicer):

    async def DispatchVoDTask(self, 
                              request: transcoding_pb2.DispatchVoDRequest, 
                              context: grpc.aio.ServicerContext
    ) -> transcoding_pb2.DispatchVoDReply:
        logger.info("Received DispatchVodTask {request.taskid}")
        print(request)
        # 这里将具体的任务请求加入到队列中
        queue_list.append(request)
        logger.info("Add {request.taskid} to queue.")
        return transcoding_pb2.DispatchVoDReply(taskid=request.taskid)

# async def FinishTask(self, request, context):
#     logger.info("Finished task.")
#     print(request)
#     return transcoding_pb2.FinishVoDReply()

async def serve() -> None:
    server = grpc.aio.server()
    transcoding_pb2_grpc.add_TranscoderServicer_to_server(Transcoder(), server)
    listen_addr = "[::]:50051"
    server.add_insecure_port(listen_addr)
    logger.info(f"Listening on {listen_addr}")
    await server.start()

    async def server_graceful_exit() -> None:
        await server.stop(3)
    
    _cleanup_coroutines.append(server_graceful_exit)
    await server.wait_for_termination()

    
    
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(serve())
    finally:
        loop.run_until_complete(asyncio.gather(*_cleanup_coroutines))
        loop.close()