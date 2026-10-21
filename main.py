from flask import Flask
from endpoints.wobc import wobc_bp
from endpoints.wnyc import wnyc_bp
from endpoints.wnpr import wnpr_bp
from endpoints.root import root_bp


def create_app():
    app = Flask(__name__)

    # Register your single-file blueprints
    app.register_blueprint(wobc_bp, url_prefix="/radiocal")
    app.register_blueprint(root_bp)
    app.register_blueprint(wnyc_bp, url_prefix="/radiocal")
    app.register_blueprint(wnpr_bp, url_prefix="/radiocal")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8090, debug=True)
