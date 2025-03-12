from astropy.coordinates import ICRS, GCRS
from astropy.time import Time
import astropy.units as u

def skyfield_to_icrs(skyfield_position):
    """将 Skyfield 的位置转换为 astropy 的 ICRS 坐标。"""
    return ICRS(
        x=skyfield_position.au[0] * u.au,
        y=skyfield_position.au[1] * u.au,
        z=skyfield_position.au[2] * u.au,
        representation_type='cartesian'
    )

def icrs_to_gcrs(icrs_coord, obstime):
    """将 ICRS 坐标转换为 GCRS 坐标。"""
    return icrs_coord.transform_to(GCRS(obstime=Time(obstime))).cartesian

def convert_au_to_km(icrs_coord):
    """将 ICRS 坐标中的 AU 单位转换为 km 单位。"""
    au_to_km = 149597870.7  # 1 au in km
    return ICRS(
        x=icrs_coord.x.value * au_to_km * u.km,
        y=icrs_coord.y.value * au_to_km * u.km,
        z=icrs_coord.z.value * au_to_km * u.km,
        representation_type='cartesian'
    )