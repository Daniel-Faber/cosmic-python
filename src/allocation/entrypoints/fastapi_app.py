from fastapi import FastAPI, encoders, Response
from fastapi.responses import JSONResponse
from allocation.domain import commands
from allocation.service_layer.handlers import InvalidSku
from allocation import bootstrap, views

app = FastAPI(title=__name__)
bus = bootstrap.bootstrap()


@app.post("/add_batch")
def add_batch(cmd: commands.CreateBatch):
    bus.handle(cmd)
    return Response(content="OK", status_code=201)


@app.post("/allocate")
def allocate_endpoint(cmd: commands.Allocate):
    try:
        bus.handle(cmd)
    except InvalidSku as e:
        return JSONResponse(content={"message": str(e)}, status_code=400)

    return Response(content="OK", status_code=202)


@app.get("/allocations/{orderid}")
def allocations_view_endpoint(orderid: str):
    result = views.allocations(orderid, bus.uow)
    if not result:
        return Response(content="not found", status_code=404)
    return encoders.jsonable_encoder(result)