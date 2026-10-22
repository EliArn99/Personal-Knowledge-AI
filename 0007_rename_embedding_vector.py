from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        (
            "documents",
            "0006_remove_documentchunk_embedding_and_more",
        ),
    ]

    operations = [
        migrations.RenameField(
            model_name="documentchunk",
            old_name="embedding_vector",
            new_name="embedding",
        ),
    ]