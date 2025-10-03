from django.db import models


class LegacyExtrusora(models.Model):
    id = models.IntegerField(primary_key=True, db_column="Id")
    nombre = models.TextField(db_column="Extrusora", blank=True, null=True)
    bloqueado = models.TextField(db_column="Bloqueado", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "extrusoras"

    def __str__(self) -> str:
        return self.nombre or f"Extrusora {self.id}"


class LegacyProductQuerySet(models.QuerySet):
    def usable(self):
        return self.exclude(descripcion__isnull=True).exclude(descripcion__startswith="*TRIAL")


class LegacyProduct(models.Model):
    id = models.IntegerField(primary_key=True, db_column="Id")
    extrusora = models.ForeignKey(
        LegacyExtrusora,
        db_column="Idextrusora",
        related_name="productos",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
    )
    linea_id = models.IntegerField(db_column="Idlinea", blank=True, null=True)
    tipo_id = models.IntegerField(db_column="Idtipo", blank=True, null=True)
    descripcion = models.TextField(db_column="Descripci_n", blank=True, null=True)
    fecha_creacion = models.TextField(db_column="Fecha_creacion", blank=True, null=True)

    objects = LegacyProductQuerySet.as_manager()

    class Meta:
        managed = False
        db_table = "productos"

    def __str__(self) -> str:
        return self.descripcion or f"Producto {self.id}"


class LegacyFrame(models.Model):
    id = models.IntegerField(primary_key=True, db_column="Id")
    product_id = models.IntegerField(db_column="idproducto", blank=True, null=True)
    descripcion = models.TextField(db_column="Descripci_n", blank=True, null=True)
    predeterminado = models.TextField(db_column="Predeterminado", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "marco"

    def __str__(self) -> str:
        return self.descripcion or f"Marco {self.id}"


class LegacyLeaf(models.Model):
    id = models.IntegerField(primary_key=True, db_column="Id")
    marco_id = models.IntegerField(db_column="idmarco", blank=True, null=True)
    descripcion = models.TextField(db_column="Descripci_n", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "hoja"

    def __str__(self) -> str:
        return self.descripcion or f"Hoja {self.id}"


class LegacyInterior(models.Model):
    id = models.IntegerField(primary_key=True, db_column="Id")
    hoja_id = models.IntegerField(db_column="Idhoja", blank=True, null=True)
    descripcion = models.TextField(db_column="Descripci_n", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "interior"

    def __str__(self) -> str:
        return self.descripcion or f"Interior {self.id}"


class LegacyContravidrio(models.Model):
    id = models.IntegerField(primary_key=True, db_column="Id")
    interior_id = models.IntegerField(db_column="idinterior", blank=True, null=True)
    descripcion = models.TextField(db_column="Descripci_n", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "contravidrio"

    def __str__(self) -> str:
        return self.descripcion or f"Contravidrio {self.id}"


class LegacyMosquitero(models.Model):
    id = models.IntegerField(primary_key=True, db_column="Id")
    hoja_id = models.IntegerField(db_column="idhoja", blank=True, null=True)
    descripcion = models.TextField(db_column="Descripci_n", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mosquitero"

    def __str__(self) -> str:
        return self.descripcion or f"Mosquitero {self.id}"


class LegacyVidrioRepartido(models.Model):
    id = models.IntegerField(primary_key=True, db_column="Id")
    interior_id = models.IntegerField(db_column="idinterior", blank=True, null=True)
    descripcion = models.TextField(db_column="Descripci_n", blank=True, null=True)

    class Meta:
        managed = False
        db_table = "vidrio_repartido"

    def __str__(self) -> str:
        return self.descripcion or f"Vidrio Repartido {self.id}"