def ecliptic_lon_lat(body, t):
    astrometric = eph['earth'].at(t).observe(body).apparent()
    ra, dec, distance = astrometric.radec()
    ra_rad = ra.radians
    dec_rad = dec.radians
    eps = np.radians(23.4392911)
    lon = np.degrees(
        np.arctan2(
            np.sin(ra_rad) * np.cos(eps) + np.tan(dec_rad) * np.sin(eps),
            np.cos(ra_rad),
        )
    ) % 360
    lat = np.degrees(
        np.arcsin(
            np.sin(dec_rad) * np.cos(eps)
            - np.cos(dec_rad) * np.sin(eps) * np.sin(ra_rad)
        )
    )
    return float(lon), float(lat)
