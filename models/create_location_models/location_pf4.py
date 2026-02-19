from models.create_location_models.model_location_pg import FloorConfig, KeyLoc

def list_config_pf4() -> list:
	config_pf4 = [
		#PF4
		FloorConfig(
			location_name = ['Z' + str(i) + j for i in range(401, 417) for j in ['A', 'B', 'C'] if 401 <= i <= 408 or 413 <= i <= 416] +\
			 ['Z' + str(i) + j for i in range(409, 413) for j in ['A', 'B']],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF4_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF4,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#PF4 WW
		FloorConfig(
			location_name = ['FZ4' + str(i).zfill(2) for i in [3, 4, 7, 8, 11, 12, 15, 16]],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF4_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF4,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = KeyLoc.Note.DUONG_LUONG
			)
	]

	return config_pf4