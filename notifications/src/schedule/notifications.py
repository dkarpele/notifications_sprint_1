from services.connections import get_broker

routing_key = 'user-reporting.v1.likes-for-reviews'


async def likes_for_reviews():
    broker = await get_broker()
    await broker.produce(routing_key=routing_key,
                         data={'hello': 1},
                         correlation_id=1)
