from flask import Flask, request, url_for, redirect, Response,render_template
import oracledb


def create_app():
   app =Flask(__name__)
   app.config.from_mapping(
      SECRET_KEY= 'mikey',#para definir las sesiones de la app
   )


   from . import funcionamiento

   app.register_blueprint(funcionamiento.bp)

   @app.route('/')
   def index():
      return render_template("index.html")
   
   if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2204, threaded=True)

   return (app)
