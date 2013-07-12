import tornado.ioloop
import tornado.web
import tornado.httpserver
import routes.index
import routes.harvest
import routes.data
import routes.reports
import routes.projects
import os
import logging


class Application(tornado.web.Application):


	def __init__(self):
		handlers = [
		(r"/", routes.index.Index), 
		(r"/update", routes.harvest.UpdateHarvest),
		(r"/employees", routes.index.ShowEmployees),
		(r"/clients", routes.index.ShowClients),
		(r"/projects", routes.index.ShowProjects),
		(r"/projects/update", routes.projects.UpdateProjects),
		(r"/bookings", routes.index.ShowWeeklyBookings),
		(r"/weekly-report", routes.index.WeeklyReport),
		(r"/weekly-report/refresh/employee", routes.reports.EmployeeWeeklyData),
		(r"/weekly-report/refresh/project", routes.reports.ProjectWeeklyData),		
		#Statics
		(r"/statics/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'statics/')}),
		(r"/css/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'statics/css/')}),
		(r"/js/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'statics/js/')}),
		(r"/img/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'statics/img/')}),
        (r"/font/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'statics/font/')}),
        #Files
        (r"/files/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'files/')}),
        (r"/uploads/(.*)", tornado.web.StaticFileHandler, {"path": os.path.join(os.path.dirname(__file__), 'files/')}),

		]
	
		settings = dict(
			site_title="Project Reporting", 
			debug=True,
			template_path=os.path.join(os.path.dirname(__file__), 'templates')
			)

		tornado.web.Application.__init__(self, handlers, **settings)



def main():
	logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', filename="./server.log", level=logging.DEBUG)
	report_app = Application()
	http_server = tornado.httpserver.HTTPServer(report_app)
	http_server.listen(8000)
	tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
	main()

