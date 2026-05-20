if user_input is not None:
    host = user_input["host"].strip()
    name = user_input["name"].strip() or "Skylight Hyperspot"

    await self.async_set_unique_id(host)
    self._abort_if_unique_id_configured()

    return self.async_create_entry(
        title=name,
        data={
            "host": host,
            "name": name,
        },
    )
