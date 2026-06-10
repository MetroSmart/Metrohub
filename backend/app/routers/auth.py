from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session, joinedload
from jose import JWTError

from app.database import get_db
from app.schemas.auth import TokenResponse, PerfilResponse, CambioPasswordPrimerIngreso
from app.services import auth_service
from app.models.usuario import Usuario
from app.models.acceso_chofer import AccesoChofer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def obtener_usuario_actual(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        return auth_service.decodificar_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    sesion = auth_service.autenticar(db, form.username, form.password)
    if not sesion:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Correo o contraseña incorrectos")
    token = auth_service.crear_token({
        "sub":       sesion["email"],
        "rol":       sesion["rol"],
        "nombre":    sesion["nombre"],
        "chofer_id": sesion["chofer_id"],
    })
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        rol=sesion["rol"],
        nombre=sesion["nombre"],
        chofer_id=sesion["chofer_id"],
        debe_cambiar_password=sesion.get("debe_cambiar_password", False),
    )


@router.get("/me", response_model=PerfilResponse)
def obtener_perfil(usuario: dict = Depends(obtener_usuario_actual),
                   db: Session = Depends(get_db)):
    if usuario["rol"] == "chofer":
        acceso = (
            db.query(AccesoChofer)
            .options(joinedload(AccesoChofer.chofer))
            .filter(AccesoChofer.email == usuario["email"])
            .first()
        )
        if not acceso or not acceso.chofer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="Acceso de chofer no encontrado")
        return PerfilResponse(
            email=acceso.email,
            rol="chofer",
            nombre=acceso.chofer.nombres,
            apellidos=acceso.chofer.apellidos,
            chofer_id=acceso.chofer_id,
            debe_cambiar_password=acceso.debe_cambiar_password,
        )

    registro = db.query(Usuario).filter(Usuario.email == usuario["email"]).first()
    if not registro:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return PerfilResponse(
        email=registro.email,
        rol=registro.rol,
        nombre=registro.nombre,
        apellidos=registro.apellidos,
        chofer_id=None,
        debe_cambiar_password=False,
    )


@router.post("/cambiar-password-primer-ingreso")
def cambiar_password_primer_ingreso(
    datos: CambioPasswordPrimerIngreso,
    usuario: dict = Depends(obtener_usuario_actual),
    db: Session = Depends(get_db),
):
    if usuario["rol"] != "chofer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Solo los choferes pueden usar este endpoint")
    try:
        auth_service.cambiar_password_primer_ingreso(
            db,
            usuario["email"],
            datos.password_actual,
            datos.password_nueva,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return {"mensaje": "Contraseña actualizada correctamente", "debe_cambiar_password": False}
