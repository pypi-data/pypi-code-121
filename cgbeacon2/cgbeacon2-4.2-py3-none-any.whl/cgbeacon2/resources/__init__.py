import pkg_resources

###### Files ######
test_snv_vcf = "resources/demo/test_trio.vcf.gz"
test_sv_vcf = "resources/demo/test_trio.SV.vcf.gz"
empty_vcf = "resources/demo/empty.SV.vcf.gz"
test_bnd_sv_vcf = "resources/demo/BND.SV.vcf"
panel1 = "resources/demo/panel1.bed"
panel2 = "resources/demo/panel2.bed"
variants_add_schema = "resources/add_variants_request_schema.json"

###### Paths ######
test_snv_vcf_path = pkg_resources.resource_filename("cgbeacon2", test_snv_vcf)
test_sv_vcf_path = pkg_resources.resource_filename("cgbeacon2", test_sv_vcf)
test_empty_vcf_path = pkg_resources.resource_filename("cgbeacon2", empty_vcf)
test_bnd_vcf_path = pkg_resources.resource_filename("cgbeacon2", test_bnd_sv_vcf)
panel1_path = pkg_resources.resource_filename("cgbeacon2", panel1)
panel2_path = pkg_resources.resource_filename("cgbeacon2", panel2)
variants_add_schema_path = pkg_resources.resource_filename("cgbeacon2", variants_add_schema)
