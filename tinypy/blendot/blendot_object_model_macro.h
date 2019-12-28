/*
   the following is an incomprehensible blob of hacks and workarounds to compensate for many of the fallencies in C++. As a plus, this macro pretty much alone defines the object model.
*/

#define REVERSE_GET_PROPERTY_LIST                                  \
public:                                                            \
	_FORCE_INLINE_ bool _is_gpl_reversed() const { return true; }; \
                                                                   \
private:

#define UNREVERSE_GET_PROPERTY_LIST                                 \
public:                                                             \
	_FORCE_INLINE_ bool _is_gpl_reversed() const { return false; }; \
                                                                    \
private:

#define GDCLASS(m_class, m_inherits)                                                                                                    \
private:                                                                                                                                \
	void operator=(const m_class &p_rval) {}                                                                                            \
	mutable StringName _class_name;                                                                                                     \
	friend class ClassDB;                                                                                                               \
                                                                                                                                        \
public:                                                                                                                                 \
	virtual String get_class() const {                                                                                                  \
		return String(#m_class);                                                                                                        \
	}                                                                                                                                   \
	virtual const StringName *_get_class_namev() const {                                                                                \
		if (!_class_name)                                                                                                               \
			_class_name = get_class_static();                                                                                           \
		return &_class_name;                                                                                                            \
	}                                                                                                                                   \
	static _FORCE_INLINE_ void *get_class_ptr_static() {                                                                                \
		static int ptr;                                                                                                                 \
		return &ptr;                                                                                                                    \
	}                                                                                                                                   \
	static _FORCE_INLINE_ String get_class_static() {                                                                                   \
		return String(#m_class);                                                                                                        \
	}                                                                                                                                   \
	static _FORCE_INLINE_ String get_parent_class_static() {                                                                            \
		return m_inherits::get_class_static();                                                                                          \
	}                                                                                                                                   \
	static void get_inheritance_list_static(List<String> *p_inheritance_list) {                                                         \
		m_inherits::get_inheritance_list_static(p_inheritance_list);                                                                    \
		p_inheritance_list->push_back(String(#m_class));                                                                                \
	}                                                                                                                                   \
	static String get_category_static() {                                                                                               \
		String category = m_inherits::get_category_static();                                                                            \
		if (_get_category != m_inherits::_get_category) {                                                                               \
			if (category != "")                                                                                                         \
				category += "/";                                                                                                        \
			category += _get_category();                                                                                                \
		}                                                                                                                               \
		return category;                                                                                                                \
	}                                                                                                                                   \
	static String inherits_static() {                                                                                                   \
		return String(#m_inherits);                                                                                                     \
	}                                                                                                                                   \
	virtual bool is_class(const String &p_class) const { return (p_class == (#m_class)) ? true : m_inherits::is_class(p_class); }       \
	virtual bool is_class_ptr(void *p_ptr) const { return (p_ptr == get_class_ptr_static()) ? true : m_inherits::is_class_ptr(p_ptr); } \
                                                                                                                                        \
	static void get_valid_parents_static(List<String> *p_parents) {                                                                     \
                                                                                                                                        \
		if (m_class::_get_valid_parents_static != m_inherits::_get_valid_parents_static) {                                              \
			m_class::_get_valid_parents_static(p_parents);                                                                              \
		}                                                                                                                               \
                                                                                                                                        \
		m_inherits::get_valid_parents_static(p_parents);                                                                                \
	}                                                                                                                                   \
                                                                                                                                        \
protected:                                                                                                                              \
	_FORCE_INLINE_ static void (*_get_bind_methods())() {                                                                               \
		return &m_class::_bind_methods;                                                                                                 \
	}                                                                                                                                   \
                                                                                                                                        \
public:                                                                                                                                 \
	static void initialize_class() {                                                                                                    \
		static bool initialized = false;                                                                                                \
		if (initialized)                                                                                                                \
			return;                                                                                                                     \
		m_inherits::initialize_class();                                                                                                 \
		ClassDB::_add_class<m_class>();                                                                                                 \
		if (m_class::_get_bind_methods() != m_inherits::_get_bind_methods())                                                            \
			_bind_methods();                                                                                                            \
		initialized = true;                                                                                                             \
	}                                                                                                                                   \
                                                                                                                                        \
protected:                                                                                                                              \
	virtual void _initialize_classv() {                                                                                                 \
		initialize_class();                                                                                                             \
	}                                                                                                                                   \
	_FORCE_INLINE_ bool (Object::*_get_get() const)(const StringName &p_name, Variant &) const {                                        \
		return (bool (Object::*)(const StringName &, Variant &) const) & m_class::_get;                                                 \
	}                                                                                                                                   \
	virtual bool _getv(const StringName &p_name, Variant &r_ret) const {                                                                \
		if (m_class::_get_get() != m_inherits::_get_get()) {                                                                            \
			if (_get(p_name, r_ret))                                                                                                    \
				return true;                                                                                                            \
		}                                                                                                                               \
		return m_inherits::_getv(p_name, r_ret);                                                                                        \
	}                                                                                                                                   \
	_FORCE_INLINE_ bool (Object::*_get_set() const)(const StringName &p_name, const Variant &p_property) {                              \
		return (bool (Object::*)(const StringName &, const Variant &)) & m_class::_set;                                                 \
	}                                                                                                                                   \
	virtual bool _setv(const StringName &p_name, const Variant &p_property) {                                                           \
		if (m_inherits::_setv(p_name, p_property)) return true;                                                                         \
		if (m_class::_get_set() != m_inherits::_get_set()) {                                                                            \
			return _set(p_name, p_property);                                                                                            \
		}                                                                                                                               \
		return false;                                                                                                                   \
	}                                                                                                                                   \
	_FORCE_INLINE_ void (Object::*_get_get_property_list() const)(List<PropertyInfo> * p_list) const {                                  \
		return (void (Object::*)(List<PropertyInfo> *) const) & m_class::_get_property_list;                                            \
	}                                                                                                                                   \
	virtual void _get_property_listv(List<PropertyInfo> *p_list, bool p_reversed) const {                                               \
		if (!p_reversed) {                                                                                                              \
			m_inherits::_get_property_listv(p_list, p_reversed);                                                                        \
		}                                                                                                                               \
		p_list->push_back(PropertyInfo(Variant::NIL, get_class_static(), PROPERTY_HINT_NONE, String(), PROPERTY_USAGE_CATEGORY));       \
		if (!_is_gpl_reversed())                                                                                                        \
			ClassDB::get_property_list(#m_class, p_list, true, this);                                                                   \
		if (m_class::_get_get_property_list() != m_inherits::_get_get_property_list()) {                                                \
			_get_property_list(p_list);                                                                                                 \
		}                                                                                                                               \
		if (_is_gpl_reversed())                                                                                                         \
			ClassDB::get_property_list(#m_class, p_list, true, this);                                                                   \
		if (p_reversed) {                                                                                                               \
			m_inherits::_get_property_listv(p_list, p_reversed);                                                                        \
		}                                                                                                                               \
	}                                                                                                                                   \
	_FORCE_INLINE_ void (Object::*_get_notification() const)(int) {                                                                     \
		return (void (Object::*)(int)) & m_class::_notification;                                                                        \
	}                                                                                                                                   \
	virtual void _notificationv(int p_notification, bool p_reversed) {                                                                  \
		if (!p_reversed)                                                                                                                \
			m_inherits::_notificationv(p_notification, p_reversed);                                                                     \
		if (m_class::_get_notification() != m_inherits::_get_notification()) {                                                          \
			_notification(p_notification);                                                                                              \
		}                                                                                                                               \
		if (p_reversed)                                                                                                                 \
			m_inherits::_notificationv(p_notification, p_reversed);                                                                     \
	}                                                                                                                                   \
                                                                                                                                        \
private:

#define OBJ_CATEGORY(m_category)                                        \
protected:                                                              \
	_FORCE_INLINE_ static String _get_category() { return m_category; } \
                                                                        \
private:

#define OBJ_SAVE_TYPE(m_class)                                 \
public:                                                        \
	virtual String get_save_class() const { return #m_class; } \
                                                               \
private:

