def _clear_container(service_client, name):
    container_client = service_client.get_container_client(name)
    items = container_client.list_blobs()
    for item in items:
        container_client.delete_blob(item.name)


def test_blob(context):
    client = context.blob_client
    service_client = client.service_client

    # Clear previous state
    _clear_container(service_client, client.settings.image_container)
    _clear_container(service_client, client.settings.process_container)
    _clear_container(service_client, client.settings.public_container)

    path = "banana"

    # Add one image
    client.put_image(path, "whatever", "stg")

    # Check added
    image_container_client = service_client.get_container_client(client.settings.image_container)
    images = image_container_client.list_blobs()
    assert sum(1 for x in images) == 1

    # Check public is empty
    public_container_client = service_client.get_container_client(client.settings.public_container)
    images = public_container_client.list_blobs()
    assert sum(1 for x in images) == 0

    # Make 1 image public and check added to the public container
    client.make_public(path)
    images = public_container_client.list_blobs()
    assert sum(1 for x in images) == 1

    # Remove from public and check effectively removed
    client.remove_from_public(path)
    images = public_container_client.list_blobs()
    assert sum(1 for x in images) == 0


def test_caching(context):
    client = context.blob_client
    path = "cached_item"
    client.cache(path, "whatever")
    assert client.get_cached(path, 1) is not None
    assert client.get_cached(path, 0) is None
    assert client.get_cached(path, 60) is not None
    assert client.get_cached("nope", 1) is None
