import time

import gigapipe

gigapipe.client_secret = "gigapipe_sk_6q9QLldhDmrWou4nlIFDWhULEMGBYJTI5lweMlXxC3A"

gigapipe = gigapipe.GigapipeClient(client_id="gigapipe_pk_lEAYfmA2U6Aa04ckt5PnEw")


### /users/me (get)

print('\n### User get info')
print(gigapipe.users.get_info())

# invite_object = {
#     "email": "asdsa@asdasd.es",
#     "organization_name": "gigapipe",
# }
#
# response = gigapipe.invites.send_invite(invite_object)
#
# print('\n### Invites send')
# print(response)


t_object = {
    'tax_type': 'au_abn',
    'tax_value': '12345678912'
}

print('\n### Post tax id')
print(gigapipe.stripe.post_tax_id(t_object))
print(gigapipe.stripe.get_tax_id())
print(gigapipe.stripe.delete_tax_id())
print(gigapipe.stripe.get_tax_id())


# gigapipe.clusters.expand_disk('cluster2', disk_id=9, payload={'size': 10.0})

# ### /users/change-password (patch)
#
# password_object = {
#     "new_password": "Qwer123?",
#     "new_password_verification": "Qwer123?",
#     "old_password": "Iwimd546?"
# }
#
# response = gigapipe.users.change_password(password_object)
#
# print('\n### Users change password')
# print(response)
#
#
# ### /users (patch)
#
# user_object = {
#     "first_name": "Barraca",
#     "last_name": "Hernandez",
# }
#
# response = gigapipe.users.update_name(user_object)
#
# print('\n### User update name')
# print(response)
#
# ### /users/me/permissions (get)
# print('\n### User permissions')
# print(gigapipe.users.get_permissions())
#
#
# ### /users/upcoming-invoice (get)
# print('\n### User invoice')
# print(gigapipe.users.get_upcoming_invoice())
#
#
# # ### /users (delete)
# # print('\n### Delete User')
# # print(gigapipe.users.delete_user())
#
#
# ### /organizations/users (get)
# print('\n### Organizations users')
# print(gigapipe.organizations.get_users())
#
# ### /organizations/invites (get)
# print('\n### Organizations invites')
# print(gigapipe.organizations.get_invites())
#
# # ### /organizations (delete)
# # print('\n### Organizations delete')
# # print(gigapipe.organizations.delete_organization())
#
# ### /users/upcoming-invoice (get)
# print('\n### Organizations invoice')
# print(gigapipe.organizations.get_upcoming_invoice())
#
# ### /invites (post)
#
# invite_object = {
#     "email": "asdsa@asdasd.es",
#     "organization_name": "gigapipe",
# }
#
# response = gigapipe.invites.send_invite(invite_object)
#
# print('\n### Invites send')
# print(response)
#
#
# ### /invites (delete)
# response = gigapipe.invites.delete_invite("asdsa@asdasd.es")
#
# print('\n### Invites delete')
# print(response)
#
#
# ### /roles/switch (post)
#
# role_object = {
#     "user_email": "test@a.com",
#     "role_name": "Admin"
# }
#
# response = gigapipe.roles.switch(role_object)
#
# print('\n### Roles switch')
# print(response)
#
#
# ### /machines (get)
#
# response = gigapipe.root.get_machines(provider_id=2, region_id=4)
#
# print('\n### Get machines')
# print(response)
#
# ### /machines/{id} (get)
#
# response = gigapipe.root.get_machine(machine_id=1)
#
# print('\n### Get Machine')
# print(response)
#
#
# ### /providers (get)
#
# response = gigapipe.root.get_providers()
#
# print('\n### Get Providers')
# print(response)
#
#
# ### /regions (get)
#
# response = gigapipe.root.get_regions(provider_id=2)
#
# print('\n### Get Regions')
# print(response)
#
# ### /disk-types (get)
#
# response = gigapipe.root.get_disk_types(provider_id=2, region_id=4)
#
# print('\n### Disk types')
# print(response)
#
#
# # ### /clusters (post)
# #
# # response = gigapipe.clusters.create_cluster({
# #     "name": "Cluster John",
# #     "machine_id": 1,
# #     "clickhouse": {
# #         "shards": 3,
# #         "replicas": 1,
# #         "disks": [
# #             {
# #                 "type": "gp2",
# #                 "size": 150.0,
# #                 "unit": "GB"
# #             }
# #         ],
# #         "admin": {
# #             "username": "john",
# #             "password": "johnpw"
# #         }
# #     },
# #     "provider_id": 2,
# #     "region_id": 4
# # })
# #
# # print('\n### Create cluster')
# # print(response)
#
# # ### /clusters (get)
# #
# # response = gigapipe.clusters.get_clusters()
# #
# # print('\n### Get clusters')
# # print(response)
# #
# # ### /clusters/{slug} (get)
# #
# # response = gigapipe.clusters.get_cluster(cluster_slug='cluster-john')
# #
# # print('\n### Get cluster')
# # print(response)
# #
# # ### /clusters/{slug}/query (get)
# #
# # response = gigapipe.clusters.get_cluster(cluster_slug='cluster-john')
# #
# # print('\n### Get cluster')
# # print(response)
#
# # ### /clusters/{slug}/query (get)
# #
# # response = gigapipe.clusters.query_cluster(cluster_slug='cluster-john', query='SELECT now()')
# #
# # print('\n### Query cluster')
# # print(response)
# #
# #
# # ### /clusters/{slug}/metadata (get)
# #
# # response = gigapipe.clusters.get_metadata(cluster_slug='cluster-john')
# #
# # print('\n### Query metadata')
# # print(response)
#
# # ### /clusters/{slug}/stop (get)
# #
# # response = gigapipe.clusters.stop_cluster(cluster_slug='cluster-john')
# #
# # print('\n### Stop cluster')
# # print(response)
# #
# # time.sleep(10)
# #
# # ### /clusters/{slug}/start (get)
# #
# # response = gigapipe.clusters.resume_cluster(cluster_slug='cluster-john')
# #
# # print('\n### Start')
# # print(response)
#
# # ### /clusters/{slug}/scale/nodes (get)
# #
# # response = gigapipe.clusters.scale_nodes('cluster-john', payload={
# #     "new_shards": 1,
# #     "new_replicas": 1
# # })
# #
# # print('\n### Scale')
# # print(response)
#
# ### /clusters/{slug}/disks (patch)
#
# response = gigapipe.clusters.add_disks('cluster-john', payload=[{
#     "autoscale_type": "%",
#     "autoscale_value": 10,
#     "type": "gp2",
#     "size": 10.0,
#     "unit": "GB"
# }])
#
# print('\n### Add disks')
# print(response)
#
# ### /clusters/{slug}/machines (patch)
#
# response = gigapipe.clusters.autoscale_disk('cluster-john', {
#     "autoscale_type": "GiB",
#     "autoscale_value": 15,
#     "id": 8
# })
#
# print('\n### Autoscale disk')
# print(response)
#
# ### Get autoscale
#
# response = gigapipe.clusters.get_autoscaling('cluster-john', disk_id=8)
#
# print('\n### Autoscale disk GET')
# print(response)
#
# ### Get autoscale
#
# response = gigapipe.clusters.delete_autoscaling('cluster-john', disk_id=8)
#
# print('\n### Delete autoscaling')
# print(response)
#
# ### /clusters/{slug}/machines (patch)
#
# response = gigapipe.clusters.change_machine('cluster-john', machine_id=2)
#
# print('\n### Change machine')
# print(response)
#
# ### /clusters/costs/all (get)
#
# response = gigapipe.clusters.get_costs()
#
# print('\n### Get costs')
# print(response)
#
# ### /clusters/{slug}/transferl (get)
#
# response = gigapipe.clusters.transfer_cluster(cluster_slug='cluster-john', email='target_user@gmail.com')
#
# print('\n### Transfer')
# print(response)
#
#
# ### delete cluster
#
# response = gigapipe.clusters.delete_cluster(cluster_slug='cluster-john')
#
# print('\n### delete cluster')
# print(response)