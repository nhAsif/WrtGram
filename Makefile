include $(TOPDIR)/rules.mk

PKG_NAME:=wrtgram

PKG_VERSION:=2.0
PKG_RELEASE:=1

PKG_LICENSE:=GPL-2.0

include $(INCLUDE_DIR)/package.mk

define Package/wrtgram
  SECTION:=net
  CATEGORY:=Network
  TITLE:=Telegram BOT for openwrt
  URL:=https://github.com/nhAsif/WrtGram
  PKGARCH:=all
  TITLE:=Telegram for openwrt BOT
endef

define Package/wrtgram/description
  Telegram for use in openwrt. Its a BOT
  that executes selected commands in your router.
  Version: $(PKG_VERSION)-$(PKG_RELEASE)
  Info   : https://github.com/nhAsif/WrtGram
endef

define Package/wrtgram/conffiles
/etc/config/wrtgram
endef

define Build/Configure
endef

define Build/Compile
endef

define Package/wrtgram/install
	$(INSTALL_DIR) $(1)/etc/init.d
	$(INSTALL_BIN) ./etc/init.d/telegram_bot \
			./etc/init.d/lanports \
			./etc/init.d/hosts_scan \
		$(1)/etc/init.d

	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_CONF) ./etc/config/wrtgram \
		$(1)/etc/config/wrtgram
	
	$(INSTALL_DIR) $(1)/etc/wrtgram
	$(INSTALL_CONF) ./etc/wrtgram/macaddr.ignore \
		$(1)/etc/wrtgram/macaddr.ignore

	$(INSTALL_DIR) $(1)/usr/share/wrtgram
	echo "$(PKG_VERSION)-$(PKG_RELEASE)" > $(1)/usr/share/wrtgram/version
	
	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins/actions
	$(INSTALL_BIN) ./usr/lib/telegramopenwrt/plugins/actions/fwr_disable \
				./usr/lib/telegramopenwrt/plugins/actions/fw_delete \
				./usr/lib/telegramopenwrt/plugins/actions/proc_stop \
				./usr/lib/telegramopenwrt/plugins/actions/fwr_enable \
				./usr/lib/telegramopenwrt/plugins/actions/fw_disable \
				./usr/lib/telegramopenwrt/plugins/actions/wifi_disable \
				./usr/lib/telegramopenwrt/plugins/actions/wifi_restart \
				./usr/lib/telegramopenwrt/plugins/actions/proc_restart \
				./usr/lib/telegramopenwrt/plugins/actions/wifi_enable \
				./usr/lib/telegramopenwrt/plugins/actions/proc_start \
				./usr/lib/telegramopenwrt/plugins/actions/fw_enable \
				./usr/lib/telegramopenwrt/plugins/actions/interface_down \
        		./usr/lib/telegramopenwrt/plugins/actions/interface_restart \
        		./usr/lib/telegramopenwrt/plugins/actions/interface_up \
		$(1)/usr/lib/wrtgram/plugins/actions
	
	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins/ctx
	$(INSTALL_BIN) ./usr/lib/telegramopenwrt/plugins/ctx/wifi_list \
				./usr/lib/telegramopenwrt/plugins/ctx/fwr_list \
				./usr/lib/telegramopenwrt/plugins/ctx/service_list \
				./usr/lib/telegramopenwrt/plugins/ctx/reboot \
				./usr/lib/telegramopenwrt/plugins/ctx/fw_list \
				./usr/lib/telegramopenwrt/plugins/ctx/interfaces_list \
		$(1)/usr/lib/wrtgram/plugins/ctx
	
	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins/help
	$(INSTALL_DATA) ./usr/lib/telegramopenwrt/plugins/help/fw_unblock \
				./usr/lib/telegramopenwrt/plugins/help/fw_add \
				./usr/lib/telegramopenwrt/plugins/help/fwr_disable \
				./usr/lib/telegramopenwrt/plugins/help/wifi_list \
				./usr/lib/telegramopenwrt/plugins/help/swports_list \
				./usr/lib/telegramopenwrt/plugins/help/fwr_list \
				./usr/lib/telegramopenwrt/plugins/help/fw_delete \
				./usr/lib/telegramopenwrt/plugins/help/get_mac \
				./usr/lib/telegramopenwrt/plugins/help/proc_stop \
				./usr/lib/telegramopenwrt/plugins/help/proc_list \
				./usr/lib/telegramopenwrt/plugins/help/get_uptime \
				./usr/lib/telegramopenwrt/plugins/help/fwr_enable \
				./usr/lib/telegramopenwrt/plugins/help/wll_list \
				./usr/lib/telegramopenwrt/plugins/help/start \
				./usr/lib/telegramopenwrt/plugins/help/ignoredmac_list \
				./usr/lib/telegramopenwrt/plugins/help/fw_disable \
				./usr/lib/telegramopenwrt/plugins/help/wifi_disable \
				./usr/lib/telegramopenwrt/plugins/help/wifi_restart \
				./usr/lib/telegramopenwrt/plugins/help/proc_restart \
				./usr/lib/telegramopenwrt/plugins/help/reboot \
				./usr/lib/telegramopenwrt/plugins/help/wifi_enable \
				./usr/lib/telegramopenwrt/plugins/help/get_ip \
				./usr/lib/telegramopenwrt/plugins/help/get_ping \
				./usr/lib/telegramopenwrt/plugins/help/fw_list \
				./usr/lib/telegramopenwrt/plugins/help/proc_start \
				./usr/lib/telegramopenwrt/plugins/help/ignoredmac_add \
				./usr/lib/telegramopenwrt/plugins/help/fw_enable \
				./usr/lib/telegramopenwrt/plugins/help/hst_list \
				./usr/lib/telegramopenwrt/plugins/help/netstat \
				./usr/lib/telegramopenwrt/plugins/help/tmate \
				./usr/lib/telegramopenwrt/plugins/help/interface_restart \
				./usr/lib/telegramopenwrt/plugins/help/interface_up \
				./usr/lib/telegramopenwrt/plugins/help/interface_down \
        		./usr/lib/telegramopenwrt/plugins/help/interfaces_list \
        		./usr/lib/telegramopenwrt/plugins/help/opkg_install \
        		./usr/lib/telegramopenwrt/plugins/help/opkg_update \
				./usr/lib/telegramopenwrt/plugins/help/cf_tunnel \
				./usr/lib/telegramopenwrt/plugins/help/cf_tunnel_stop \
		$(1)/usr/lib/wrtgram/plugins/help

	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins
	$(INSTALL_BIN) ./usr/lib/telegramopenwrt/plugins/fw_unblock \
				./usr/lib/telegramopenwrt/plugins/fw_add \
				./usr/lib/telegramopenwrt/plugins/fwr_disable \
				./usr/lib/telegramopenwrt/plugins/wifi_list \
				./usr/lib/telegramopenwrt/plugins/swports_list \
				./usr/lib/telegramopenwrt/plugins/fwr_list \
				./usr/lib/telegramopenwrt/plugins/fw_delete \
				./usr/lib/telegramopenwrt/plugins/get_mac \
				./usr/lib/telegramopenwrt/plugins/proc_stop \
				./usr/lib/telegramopenwrt/plugins/proc_list \
				./usr/lib/telegramopenwrt/plugins/get_uptime \
				./usr/lib/telegramopenwrt/plugins/fwr_enable \
				./usr/lib/telegramopenwrt/plugins/wll_list \
				./usr/lib/telegramopenwrt/plugins/start \
				./usr/lib/telegramopenwrt/plugins/ignoredmac_list \
				./usr/lib/telegramopenwrt/plugins/fw_disable \
				./usr/lib/telegramopenwrt/plugins/wifi_disable \
				./usr/lib/telegramopenwrt/plugins/wifi_restart \
				./usr/lib/telegramopenwrt/plugins/proc_restart \
				./usr/lib/telegramopenwrt/plugins/reboot \
				./usr/lib/telegramopenwrt/plugins/wifi_enable \
				./usr/lib/telegramopenwrt/plugins/get_ip \
				./usr/lib/telegramopenwrt/plugins/get_ping \
				./usr/lib/telegramopenwrt/plugins/fw_list \
				./usr/lib/telegramopenwrt/plugins/proc_start \
				./usr/lib/telegramopenwrt/plugins/ignoredmac_add \
				./usr/lib/telegramopenwrt/plugins/fw_enable \
				./usr/lib/telegramopenwrt/plugins/hst_list \
				./usr/lib/telegramopenwrt/plugins/netstat \
				./usr/lib/telegramopenwrt/plugins/tmate \
				./usr/lib/telegramopenwrt/plugins/interface_down \
        		./usr/lib/telegramopenwrt/plugins/interface_restart \
        		./usr/lib/telegramopenwrt/plugins/interface_up \
        		./usr/lib/telegramopenwrt/plugins/interfaces_list \
        		./usr/lib/telegramopenwrt/plugins/opkg_install \
        		./usr/lib/telegramopenwrt/plugins/opkg_update \
				./usr/lib/telegramopenwrt/plugins/cf_tunnel \
				./usr/lib/telegramopenwrt/plugins/cf_tunnel_stop \
		$(1)/usr/lib/wrtgram/plugins

	$(INSTALL_DIR) $(1)/sbin
	$(INSTALL_BIN) ./sbin/telebot \
				./sbin/telegram_bot \
				./sbin/telekeyboard \
				./sbin/hosts_scan \
				./sbin/typing \
				./sbin/telegram_sender \
				./sbin/lanports \
		$(1)/sbin/
endef

define Package/wrtgram/postinst
#!/bin/sh
if [ -z "$${IPKG_INSTROOT}" ]; then
	/etc/init.d/telegram_bot enable
	/etc/init.d/lanports enable
	/etc/init.d/hosts_scan enable
	/etc/init.d/telegram_bot start
	/etc/init.d/lanports start
	/etc/init.d/hosts_scan start
fi
exit 0
endef

define Package/wrtgram/prerm
#!/bin/sh
if [ -n "$${IPKG_INSTROOT}" ]; then
	/etc/init.d/telegram_bot stop
	/etc/init.d/lanports stop
	/etc/init.d/hosts_scan stop
	/etc/init.d/telegram_bot disable
	/etc/init.d/lanports disable
	/etc/init.d/hosts_scan disable
fi
exit 0
endef

$(eval $(call BuildPackage,wrtgram))
