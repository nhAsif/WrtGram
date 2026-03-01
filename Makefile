include $(TOPDIR)/rules.mk

PKG_NAME:=wrtgram

PKG_VERSION:=2.4.0
PKG_RELEASE:=1

PKG_LICENSE:=GPL-2.0

include $(INCLUDE_DIR)/package.mk

define Package/wrtgram
  SECTION:=net
  CATEGORY:=Network
  TITLE:=Telegram BOT for OpenWrt
  DEPENDS:=+curl +jsonfilter +ca-bundle +python3-light
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
	find . -type f -print0 | xargs -0 sed -i 's/\r//g'
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

	$(INSTALL_DIR) $(1)/usr/lib/wrtgram
	$(INSTALL_BIN) ./usr/lib/wrtgram/common \
		$(1)/usr/lib/wrtgram
	$(INSTALL_DATA) ./usr/lib/wrtgram/wrtapi.py \
		$(1)/usr/lib/wrtgram

	$(INSTALL_DIR) $(1)/usr/share/wrtgram
	echo "$(PKG_VERSION)-$(PKG_RELEASE)" > $(1)/usr/share/wrtgram/version
	
	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins/actions
	$(INSTALL_BIN) ./usr/lib/wrtgram/plugins/actions/fwr_disable \
				./usr/lib/wrtgram/plugins/actions/fw_delete \
				./usr/lib/wrtgram/plugins/actions/proc_stop \
				./usr/lib/wrtgram/plugins/actions/fwr_enable \
				./usr/lib/wrtgram/plugins/actions/fw_disable \
				./usr/lib/wrtgram/plugins/actions/wifi_disable \
				./usr/lib/wrtgram/plugins/actions/wifi_restart \
				./usr/lib/wrtgram/plugins/actions/proc_restart \
				./usr/lib/wrtgram/plugins/actions/wifi_enable \
				./usr/lib/wrtgram/plugins/actions/proc_start \
				./usr/lib/wrtgram/plugins/actions/fw_enable \
				./usr/lib/wrtgram/plugins/actions/interface_down \
        		./usr/lib/wrtgram/plugins/actions/interface_restart \
				./usr/lib/wrtgram/plugins/actions/interface_up \
				./usr/lib/wrtgram/plugins/actions/dashboard.py \
				./usr/lib/wrtgram/plugins/actions/ctx_relist.py \
		$(1)/usr/lib/wrtgram/plugins/actions
	
	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins/ctx
	$(INSTALL_BIN) ./usr/lib/wrtgram/plugins/ctx/wifi_list \
				./usr/lib/wrtgram/plugins/ctx/fwr_list \
				./usr/lib/wrtgram/plugins/ctx/service_list \
				./usr/lib/wrtgram/plugins/ctx/reboot \
				./usr/lib/wrtgram/plugins/ctx/fw_list \
				./usr/lib/wrtgram/plugins/ctx/interfaces_list \
				./usr/lib/wrtgram/plugins/ctx/helper.py \
		$(1)/usr/lib/wrtgram/plugins/ctx
	
	# Help directory removed (text merged into plugins)

	$(INSTALL_DIR) $(1)/usr/lib/wrtgram/plugins
	$(INSTALL_BIN) ./usr/lib/wrtgram/plugins/fw_unblock \
				./usr/lib/wrtgram/plugins/fw_add \
				./usr/lib/wrtgram/plugins/fwr_disable \
				./usr/lib/wrtgram/plugins/wifi_list \
				./usr/lib/wrtgram/plugins/swports_list \
				./usr/lib/wrtgram/plugins/fwr_list \
				./usr/lib/wrtgram/plugins/fw_delete \
				./usr/lib/wrtgram/plugins/get_mac \
				./usr/lib/wrtgram/plugins/proc_stop \
				./usr/lib/wrtgram/plugins/proc_list \
				./usr/lib/wrtgram/plugins/get_uptime \
				./usr/lib/wrtgram/plugins/fwr_enable \
				./usr/lib/wrtgram/plugins/wll_list \
				./usr/lib/wrtgram/plugins/start.py \
				./usr/lib/wrtgram/plugins/ignoredmac_list \
				./usr/lib/wrtgram/plugins/fw_disable \
				./usr/lib/wrtgram/plugins/wifi_disable \
				./usr/lib/wrtgram/plugins/wifi_restart \
				./usr/lib/wrtgram/plugins/proc_restart \
				./usr/lib/wrtgram/plugins/reboot \
				./usr/lib/wrtgram/plugins/wifi_enable \
				./usr/lib/wrtgram/plugins/get_ip \
				./usr/lib/wrtgram/plugins/get_ping \
				./usr/lib/wrtgram/plugins/fw_list.py \
				./usr/lib/wrtgram/plugins/proc_start \
				./usr/lib/wrtgram/plugins/ignoredmac_add \
				./usr/lib/wrtgram/plugins/fw_enable \
				./usr/lib/wrtgram/plugins/hst_list \
				./usr/lib/wrtgram/plugins/netstat \
				./usr/lib/wrtgram/plugins/tmate \
				./usr/lib/wrtgram/plugins/interface_down \
        		./usr/lib/wrtgram/plugins/interface_restart \
        		./usr/lib/wrtgram/plugins/interface_up \
        		./usr/lib/wrtgram/plugins/interfaces_list \
        		./usr/lib/wrtgram/plugins/opkg_install \
        		./usr/lib/wrtgram/plugins/opkg_update \
				./usr/lib/wrtgram/plugins/status.py \
				./usr/lib/wrtgram/plugins/cf_tunnel \
				./usr/lib/wrtgram/plugins/cf_tunnel_stop \
				./usr/lib/wrtgram/plugins/bw_stats \
				./usr/lib/wrtgram/plugins/version \
				./usr/lib/wrtgram/plugins/lan_scan \
				./usr/lib/wrtgram/plugins/dashboard.py \
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
	# Prune legacy help files
	if [ -d /usr/lib/wrtgram/plugins/help ]; then
		rm -rf /usr/lib/wrtgram/plugins/help
	fi

	# Prune deprecated shell plugins now replaced by python
	for f in dashboard status start fw_list; do
		if [ -f "/usr/lib/wrtgram/plugins/$$f" ] && [ -f "/usr/lib/wrtgram/plugins/$$f.py" ]; then
			rm -f "/usr/lib/wrtgram/plugins/$$f"
		fi
	done

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
if [ -z "$${IPKG_INSTROOT}" ]; then
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
