from api import config, users, permission

config.create_field("last_interaction", int)
config.create_field("last_interaction_channel", int)
config.create_field("last_interaction_user", int)
config.create_field("times_pet", int)
config.create_field("last_pet", int)

config.create_field("images", ["https://cdn.discordapp.com/attachments/1507229362678665276/1514043333939433682/image.png?ex=6a29ee3c&is=6a289cbc&hm=bade35e52ae1be7fef0c5161d3e56531769cc481bd5b2519022f939bc3759843&"])

users.new_data_field("friendliness", int)
users.new_data_field("last_friendliness_update", int)
users.new_data_field("times_pet", int)

permission.create("add_uni_images", "Add Uni Images")