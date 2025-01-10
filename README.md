# Gestor de Proyectos - GesPro

El Lic. Xavier, profesor del departamento de Computación de la facultad de ciencias exactas de la Universidad de Gulubú, se comunicó con CIMNE para solicitar el diseño de una aplicación que permita gestionar los diferentes proyectos de la materia de Desarrollo Web. Xavier plantea la siguiente situación.

Actualmente, Xavier y el resto del equipo docente de esta materia realizan seguimiento de manera individual de cada uno de los proyectos de sus alumnos. Los profesores, que pertenecen a distintos departamentos y tienen diferentes especialidades, buscan una manera más organizada de gestionar su trabajo con los estudiantes.

En base a esto, se busca crear una aplicación para centralizar los proyectos de los alumnos y permitir a los profesores ver el avance de los mismos y calificarlos.

Para utilizar la aplicación, tanto alumnos como profesores deben estar registrados para utilizar el sistema. Los alumnos deberán proporcionar su número de matrícula y la carrera que están cursando, mientras que los profesores indicarán su departamento y especialidad. El sistema solo permitirá crear cuentas de alumnos en su interfaz pública.

Los profesores deben poder crear actividades (trabajos prácticos que requieren la realización de un proyecto), las cuales deben tener nombre, consigna, fecha de entrega y nota de aprobación.

Los alumnos pueden registrar proyectos que deben estar asociados a una actividad como entrega de la misma.

Un proyecto puede ser individual o grupal. Si es grupal, se deben especificar sus integrantes, teniendo en cuenta que solo otros alumnos pueden ser parte del grupo. Debe incluirse un único enlace a un repositorio.
Una vez creado el proyecto, el profesor debe poder visualizarlo y calificarlo.

Para conveniencia del profesor, la aplicación debe permitir ver un listado de las actividades existentes (pudiendo filtrarlas por su nombre) y, para una actividad seleccionada, debería poder ver un listado de proyectos (pudiendo filtrarlos por nombre de alumno, número de matrícula, carrera y fecha).

A su vez, el alumno debe poder ver todos los proyectos de los cuales es partícipe, independientemente de si es el creador o solo un integrante del grupo. El sistema debe facilitar la búsqueda de compañeros de grupo por carrera, lo que ayudará en la formación de equipos interdisciplinarios.

## Objetivo

En este proyecto se implementará una API RESTful con Python y Flask, la cual permitirá gestionar los proyectos de los alumnos y las actividades de los profesores. Además, se implementará una capa de autenticación para los usuarios mediante JWT.

## Estructura del proyecto

```bash
gespro/
│   src/
│   ├── db.py
│   ├── models/
│   │   ├── user_model.py
│   ├── repositories/
│   │   ├── user_repository.py
│   ├── services/
│   │   ├── user_service.py
│   ├── controllers/
│   │   ├── user_controller.py
│   ├── utils/
├── tests/
│   app.py
│   config.py
```

## Requerimientos

- Python 3.10+
- Flask 3.1.0
- MySQL Connector 9.1
- Flask JWT Extended 4.7.1
- bcrypt 4.2.1
- Flask Cors 5.0.0
- Python Dotenv 1.0.1

## Instalación

1. Instalar las dependencias del proyecto:

```bash
pip install -r requirements.txt
```

2. Crear un archivo `.env` en la raíz del proyecto. El repositorio cuenta con un archivo `.env.example` que puedes utilizar como base.

3. Crear una base de datos en MySQL y configurar las credenciales en el archivo `.env`.

4. Para lanzar la aplicación, ejecutar el siguiente comando:

```bash
flask --app app run
```