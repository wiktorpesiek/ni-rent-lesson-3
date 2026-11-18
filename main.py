from pydantic import BaseModel
from typing import Dict, List

import json


class Parameters(BaseModel):
    apartments_json_path: str = 'data/apartments.json'
    tenants_json_path: str = 'data/tenants.json'
    transfers_json_path: str = 'data/transfers.json'
    bills_json_path: str = 'data/bills.json'


class Room(BaseModel):
    name: str
    area_m2: float


class Apartment(BaseModel):
    key: str
    name: str
    location: str
    area_m2: float
    rooms: Dict[str, Room]

    @staticmethod
    def from_json_file(file_path: str) -> Dict[str,'Apartment']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, dict), "Expected a dictionary of apartments"
        return {key: Apartment(**apartment) for key, apartment in data.items()}

    
class Tenant(BaseModel):
    name: str
    apartment: str
    room: str
    rent_pln: float
    deposit_pln: float
    date_agreement_from: str
    date_agreement_to: str

    @staticmethod
    def from_json_file(file_path: str) -> Dict[str,'Tenant']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, dict), "Expected a dictionary of tenants"
        return {key: Tenant(**tenant) for key, tenant in data.items()}
    

class Transfer(BaseModel):
    amount_pln: float
    date: str
    settlement_year: int | None
    settlement_month: int | None
    tenant: str

    @staticmethod
    def from_json_file(file_path: str) -> List['Transfer']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, list), "Expected a list of transfers"
        return [Transfer(**transfer) for transfer in data]


class Bill(BaseModel):
    amount_pln: float
    date_due: str
    apartment: str
    settlement_year: int
    settlement_month: int
    type: str

    @staticmethod
    def from_json_file(file_path: str) -> List['Bill']:
        data = None
        with open(file_path, 'r') as file:
            data = json.load(file)
        assert isinstance(data, list), "Expected a list of bills"
        return [Bill(**bill) for bill in data]


class ApartmentSettlement(BaseModel):
    """Miesięczne rozliczenie mieszkania: suma czynszów, suma rachunków
    oraz kwota pozostała do uregulowania za dany rok i miesiąc."""
    apartment: str
    year: int
    month: int
    total_rent_pln: float
    total_bills_pln: float
    total_due_pln: float


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)


if __name__ == '__main__':
    parameters = Parameters()
    manager = Manager(parameters)

    print('=' * 72)
    print('MIESZKANIA')
    print('=' * 72)
    print(f"{'Klucz':<16}{'Nazwa':<14}{'Adres':<20}{'Powierzchnia':>14}")
    print('-' * 72)
    for apartment in manager.apartments.values():
        print(f"{apartment.key:<16}{apartment.name:<14}{apartment.location:<20}{apartment.area_m2:>11.2f} m2")

        print()
        print(f"  Pokoje w {apartment.key}:")
        print(f"  {'Nazwa pokoju':<20}{'Powierzchnia':>14}")
        for room in apartment.rooms.values():
            print(f"  {room.name:<20}{room.area_m2:>11.2f} m2")

        print()
        print(f"  Rachunki dla {apartment.key}:")
        print(f"  {'Typ':<14}{'Okres':<10}{'Termin':<14}{'Kwota':>16}")
        for bill in manager.bills:
            if bill.apartment == apartment.key:
                period = f"{bill.settlement_year}-{bill.settlement_month:02d}"
                print(f"  {bill.type:<14}{period:<10}{bill.date_due:<14}{bill.amount_pln:>12.2f} PLN")
        print()

    print('=' * 72)
    print('NAJEMCY')
    print('=' * 72)
    print(f"{'Najemca':<12}{'Mieszkanie':<16}{'Pokój':<16}{'Czynsz':>14}{'Kaucja':>14}")
    print('-' * 72)
    for tenant in manager.tenants.values():
        print(f"{tenant.name:<12}{tenant.apartment:<16}{tenant.room:<16}{tenant.rent_pln:>10.2f} PLN{tenant.deposit_pln:>10.2f} PLN")
        print(f"  Umowa: {tenant.date_agreement_from} - {tenant.date_agreement_to}")
        print(f"  {'Data przelewu':<16}{'Okres':<10}{'Kwota':>16}")
        for transfer in manager.transfers:
            if transfer.tenant == tenant.name:
                period = f"{transfer.settlement_year}-{transfer.settlement_month:02d}"
                print(f"  {transfer.date:<16}{period:<10}{transfer.amount_pln:>12.2f} PLN")
        print()