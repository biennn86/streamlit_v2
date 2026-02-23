from models.create_location_models.model_location_pg import FloorConfig, KeyLoc

def list_config_pf3() -> list:
	config_pf3 = [
		#PF3
		FloorConfig(
			location_name =['Z' + str(i) + j for i in range(305, 313) for j in ['A', 'B']] +\
			 ['Z' + str(i) for i in range(301, 317) if 301 <= i <= 304 or 313 <= i <= 316],
			location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF3_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF3,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = None
			),
		#PF3 WW
		FloorConfig(
			location_name = ['FZ3' + str(i).zfill(2) for i in [3, 4, 7, 8, 11, 12, 15, 16]],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF3_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF3,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Status_Location.OK,
			note = KeyLoc.Note.DUONG_LUONG
			)
	]

	return config_pf3