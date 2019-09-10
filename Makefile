#
# Makefile to generate specifications
#

.PHONY: clean all json franca c

all: clean json franca franca_attributes csv c

DESTDIR?=/usr/local

json:
	./tools/vspec2json.py -i:spec/VehicleSignalSpecification.id -I ./spec ./spec/VehicleSignalSpecification.vspec vss_rel_$$(cat VERSION).json

franca:
	./tools/vspec2franca.py -v $$(cat VERSION) -i:spec/VehicleSignalSpecification.id -I ./spec ./spec/VehicleSignalSpecification.vspec vss_rel_$$(cat VERSION).fidl

franca_attributes:
	./tools/vspec2franca_attributes.py -p Vehicle.Drivetrain -n FuelSystem -v $$(cat VERSION) -i:spec/VehicleSignalSpecification.id -I ./spec ./spec/VehicleSignalSpecification.vspec vss_rel_$$(cat VERSION)_attributes.fidl

csv:
	./tools/vspec2csv.py -i:spec/VehicleSignalSpecification.id -I ./spec ./spec/VehicleSignalSpecification.vspec vss_rel_$$(cat VERSION).csv


cnative:
	./tools/vspec2cnative.py -i:./spec/VehicleSignalSpecification.id ./spec/VehicleSignalSpecification.vspec vss_rel_$$(cat VERSION).cnative

c:
	(cd ./tools/vspec2c/; make )
	./tools/vspec2c.py -i:./spec/VehicleSignalSpecification.id -I ./spec ./spec/VehicleSignalSpecification.vspec vss_rel_$$(cat VERSION).h vss_rel_$$(cat VERSION)_macro.h

clean:
	rm -f vss_rel_$$(cat VERSION).json vss_rel_$$(cat VERSION).fidl vss_rel_$$(cat VERSION).csv vss_rel_$$(cat VERSION).h
	(cd ./tools/vspec2c/; make clean)

install:
	(cd ./tools; python3 setup.py install --install-scripts=${DESTDIR}/bin)
	$(MAKE) DESTDIR=${DESTDIR} -C tools/vspec2c install
	install -d ${DESTDIR}/share/vss
	(cd spec; cp -r * ${DESTDIR}/share/vss)
