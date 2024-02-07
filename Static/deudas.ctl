OPTIONS (SKIP=1, READSIZE=10485760, LOAD=250000, BINDSIZE=10485760, ERRORS=0, DIRECT=TRUE)
LOAD DATA
INFILE 'E:\todo\2023A\BasesDeDatos\Proyecto\proyecto\Static\deudas.dat'
APPEND
INTO TABLE deudas
FIELDS TERMINATED BY '|'
TRAILING NULLCOLS
(
  id_deuda,
  cliente_id,
  monto,
  fecha_deuda TIMESTAMP 'YYYY-MM-DD HH24:MI:SS.FF',
  pagada
)