from app.schemas.search import VehicleListing


FIXTURE_LISTINGS = [
    VehicleListing(id="dubizzle-fixture-1", source_id="dubizzle", source_name="Dubizzle", source_url="https://dubai.dubizzle.com/motors/used-cars/", title="2023 Mercedes-Benz C-Class C200 GCC", price=172000, currency="AED", city="Dubai", make="Mercedes-Benz", model="C-Class", year=2023, mileage_km=38000, color="Black", specifications=["GCC"], seller_type="Dealer", warranty=True, condition_signals=["Listing claims accident-free"], freshness_days=2),
    VehicleListing(id="dubizzle-fixture-2", source_id="dubizzle", source_name="Dubizzle", source_url="https://dubai.dubizzle.com/motors/used-cars/", title="2023 Mercedes-Benz E-Class E200 GCC", price=179000, currency="AED", city="Dubai", make="Mercedes-Benz", model="E-Class", year=2023, mileage_km=47000, color="White", specifications=["GCC"], seller_type="Dealer", warranty=True, condition_signals=["Inspection report available"], freshness_days=4),
    VehicleListing(id="dubizzle-fixture-3", source_id="dubizzle", source_name="Dubizzle", source_url="https://abudhabi.dubizzle.com/motors/used-cars/", title="2023 Mercedes-Benz C-Class C300 US Specs", price=151000, currency="AED", city="Abu Dhabi", make="Mercedes-Benz", model="C-Class", year=2023, mileage_km=41000, color="Silver", specifications=["US"], seller_type="Private seller", warranty=False, condition_signals=["Imported specs", "Damage not mentioned"], freshness_days=9),
]

