#!/usr/bin/env python3
from mitmproxy import proxy, options
from mitmproxy.tools.dump import DumpMaster
from mitmproxy import ctx


class AddHeader:
    def request(self, flow):
        ctx.log.error("some ctx.log.error")
        ctx.log.error(flow.request.pretty_url)
        print("some print statement")


def start():
    myaddon = AddHeader()
    opts = options.Options(listen_host='0.0.0.0', listen_port=8080,
                           #    mode='transparent', confdir='/root/.mitmproxy')
                           confdir='/root/.mitmproxy')
    pconf = proxy.config.ProxyConfig(opts)
    m = DumpMaster(opts)
    m.server = proxy.server.ProxyServer(pconf)
    m.addons.add(myaddon)

    try:
        m.run()
    except KeyboardInterrupt:
        m.shutdown()


start()
