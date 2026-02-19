from models.create_location_models.model_location_pg import FloorConfig, KeyLoc

def list_config_pf5() -> list:
	config_pf5 = [
		#PF5 RACK
		FloorConfig(
			location_name = ['Z' + str(i) + str(j) for i in range(51010, 51170, 10) for j in ['B', 'C']] +\
			 ['Z' + str(i) + str(j) for i in range(5501, 5533) for j in ['TA', 'NA']] +\
			 ['Z' + str(i) + str(j) for i in range(52010, 52160, 10) for j in ['A', 'B', 'C']],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.ST,
			location_storage_type = KeyLoc.LocStorageType.RACK_PF,
			zone = KeyLoc.Zone.PF5_RACK,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF5,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#PF5 SÀN
		FloorConfig(
			location_name = ['Z' + str(i) + str(j) for i in range(536, 552) for j in ['', 'A']] +\
			 ['Z' + str(i) for i in range(552, 569)],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF5_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF5,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#PF5 WW
		FloorConfig(
			location_name = ['FZ' + str(i) for i in [555, 556, 559, 560, 561, 565, 566, 567, 568]],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF5_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF5,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = [],
			status_location = KeyLoc.Stauts_Location.OK,
			note = KeyLoc.Note.DUONG_LUONG
			),
		#================================================================================
		#VỊ TRÍ KHO PF5 CŨ TRƯỚC KHI XÂY RACK
		#VỊ TRÍ ĐỂ PHUY LẺ
		FloorConfig(
			location_name = ['Z5' + str(i).zfill(2) + j for i in range(1, 19) for j in ['A1', 'A2', 'B1', 'B2']],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF5_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF5,
			pallet_capacity = 1,
			stack_limit = 1,
			is_active = 0,
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#VỊ TRÍ ĐỂ PHUY CHỒNG ĐÔI
		FloorConfig(
			location_name = ['Z' + str(i) + str(j) for i in range(520, 536) for j in ['', 'A']],
		 	location_system_type = KeyLoc.LocSystemType.MK,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF5_FLOOR,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF5,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = 0,
			status_location = KeyLoc.Stauts_Location.OK,
			note = None
			),
		#VỊ TRÍ ĐƯỜNG LUỒNG
		FloorConfig(
			location_name = ['FZ' + str(i) for i in [504, 505, 506, 510, 511, 512, 516, 517, 518]],
			location_system_type = KeyLoc.LocSystemType.WW,
			rack_system_type = KeyLoc.RackSystemType.FL,
			location_storage_type = KeyLoc.LocStorageType.FLOOR,
			zone = KeyLoc.Zone.PF5_WW,
			location_category = KeyLoc.LocCategory.STORARE,
			location_product_category = KeyLoc.LocProducCategory.MK,
			name_warehouse = KeyLoc.NameWarehouse.PF5,
			pallet_capacity = 1,
			stack_limit = 2,
			is_active = 0,
			status_location = KeyLoc.Stauts_Location.OK,
			note = KeyLoc.Note.DUONG_LUONG
			),

	]

	return config_pf5