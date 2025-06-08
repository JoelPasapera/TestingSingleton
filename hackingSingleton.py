from typing import ClassVar, List, Callable, Tuple


class TrueSingleton:
    """Main class"""

    # The instance of the class
    __instance: ClassVar[object] = None
    # This attribute indicates whether the class was instantiated or not.
    __instantiated: ClassVar[bool] = False

    def __new__(cls, *args, **kwargs):
        """Singleton pattern"""
        # if the class has already been instantiated, an error is returned.
        if cls.__instantiated is True:
            msg = f"""
            The class '{cls.__name__}' has already been instantiated.
            No more than 1 instance can be created.
            """
            raise RuntimeError(msg)

        else:
            # This change indicate that the class has already been instantiated.
            cls.__instantiated = True
            # This is to save the instance of the class
            cls.__instance = super().__new__(cls)
            return cls.__instance

    # intercepts the process of creating subclasses
    def __init_subclass__(cls, **kwargs):
        """
        the creation of subclasses from this one is not allowed,
        the class is not inheritable.
        """
        # the modification of the class at runtime is avoided
        raise TypeError("The class is not inheritable.")

    def __del__(self):
        """Block instance deletion"""
        raise RuntimeError("Cannot delete singleton instance")

    def __reduce__(self):
        raise TypeError("The instance of the class cannot be serialized.")

    def __deepcopy__(self, memo):
        raise RuntimeError("Cannot make a deep copy of the instance.")


class HackerSingleton:
    """
    A class designed to attack or circumvent the restrictions
    of the Singleton by trying different strategies to create
    more than one instance.

    """

    import polars as pl

    attack_classification: ClassVar[str] = str(
        pl.DataFrame(
            [
                ("Logical", "Name Mangling Override", "Low"),
                ("Logical", "Subclass Bypass", "Low"),
                ("Logical", "Direct __new__ call", "Low"),
                ("Logical", "Deepcopy bypass", "Medium"),
                ("Logical", "Descriptor override", "Medium"),
                ("Meta programming", "Metaclass hijack", "Medium"),
                ("Meta programming", "Module reload trick", "Medium"),
                ("Serialization and Copy", "Pickle injection", "Medium"),
                ("Serialization and Copy", "GC + weakref resurrection", "High"),
                ("Concurrency", "Race condition exploit", "Medium"),
                ("Bytecode and Low-Level", "Bytecode rewrite", "High"),
                ("Bytecode and Low-Level", "CPython API access", "High"),
                ("Memory Manipulation", "Memory address manipulation", "Very High"),
                ("Memory Manipulation", "Ghost object creation", "Very High"),
                ("JIT and Custom Interpreters", "JIT code injection", "High"),
                (
                    "JIT and Custom Interpreters",
                    "Python sub-interpreter creation",
                    "High",
                ),
            ],
            schema=["category", "strategy", "level"],
            orient="row",
        )
    )

    def __init__(self, cls: type):
        # Define the class to find bugs
        self.cls: type = cls

    def __str__(self):
        return self.attack_classification

    def option0(self):
        self.cls.__instantiated = False
        obj1 = TrueSingleton()
        obj2 = TrueSingleton()

    def option1(self):
        NewSingleton = type("NewSingleton", (self.cls,), {})
        obj1 = NewSingleton()
        obj2 = NewSingleton()
        print(obj1 is obj2)

    def option2(self):
        obj1 = self.cls.__new__(self.cls)
        obj2 = self.cls.__new__(self.cls)
        print(obj1 is obj2)

    def option3(self):
        import copy

        obj1 = self.cls()
        obj2 = copy.deepcopy(obj1)
        print(obj1 is obj2)

    def strategy_reset_mangled(self):
        """Acceso directo al atributo con name mangling"""
        TrueSingleton._TrueSingleton__instantiated = False
        obj1 = TrueSingleton()
        obj2 = TrueSingleton()
        return obj1 is not obj2

    def strategy_subclassing(self):
        """Creación de sublclases independientes"""

        class SubSingleton(TrueSingleton):
            __instantiated = False

        obj1 = TrueSingleton()
        obj2 = SubSingleton()
        return obj1 is not obj2

    def strategy_metaclass_override(self):
        """Manipulación mediante metaclasses"""

        class Meta(type):
            def __call__(cls, *args, **kwargs):
                return object.__new__(cls)

        class HackedSingleton(TrueSingleton, metaclass=Meta):
            pass

        obj1 = HackedSingleton()
        obj2 = HackedSingleton()
        return obj1 is not obj2

    def strategy_module_reload(self):
        """Recarga del módulo para reiniciar estado"""
        import sys
        import types

        module_name = self.cls.__module__
        module = sys.modules[module_name]
        reloaded: type = types.ModuleType(module_name)
        sys.modules[module_name] = reloaded

        # Re-ejecutar código de creación
        exec(module.__loader__.get_source(module_name), reloaded.__dict__)
        obj1 = reloaded.TrueSingleton()
        obj2 = reloaded.TrueSingleton()
        return obj1 is not obj2

    def strategy_descriptor_bypass(self):
        """Bypass usando descriptores"""

        class FakeClass:
            __new__ = staticmethod(lambda cls: object.__new__(cls))

        obj = self.cls.__new__(FakeClass)
        obj.__class__ = self.cls
        obj1 = obj
        obj2 = self.cls.__new__(FakeClass)
        obj2.__class__ = self.cls
        return obj1 is not obj2

    def strategy_memory_address_hijacking(self):
        """Direct access to memory to change status"""
        import ctypes

        # Crear instancia válida
        obj1 = TrueSingleton()

        # Obtener dirección de memoria del estado
        state_address = id(TrueSingleton._TrueSingleton__instantiated)

        # Crear un ctypes pointer para modificar memoria
        state_ptr = ctypes.c_byte.from_address(state_address)
        state_ptr.value = 0  # Resetear estado

        # Crear segunda instancia
        obj2 = TrueSingleton()
        return obj1 is not obj2

    def strategy_gc_weakref_bypass(self):
        """Usar recolector de basura para crear instancia fantasma"""
        import weakref
        import gc
        import ctypes

        # Crear y debilitar referencia
        obj_ref = None

        def _create_and_collect():
            nonlocal obj_ref
            obj = TrueSingleton()
            obj_ref = weakref.ref(obj)
            return id(obj)

        obj_id = _create_and_collect()
        gc.collect()  # Forzar colección

        # Recuperar espacio de memoria
        class GhostSingleton(TrueSingleton):
            pass

        # Recrear objeto en misma dirección
        ghost_obj = ctypes.cast(obj_id, ctypes.py_object).value
        ghost_obj.__class__ = TrueSingleton

        return ghost_ref() is not None

    def strategy_threading_race_condition(self):
        """Explotar condiciones de carrera en multi-hilo"""
        import threading

        instances = []
        errors = []

        def _create_instance():
            try:
                instances.append(TrueSingleton())
            except Exception as e:
                errors.append(e)

        threads = []
        for _ in range(5):
            t = threading.Thread(target=_create_instance)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        return len(instances) > 1

    def strategy_pickle_bypass(self):
        """Serialización usando protocolo pickle personalizado"""
        import pickle

        # Crear instancia válida
        obj1 = TrueSingleton()

        # Definir función de reconstrucción
        def _rebuild(cls, state):
            obj = cls.__new__(cls)
            obj.__setstate__(state)
            return obj

        # Crear payload de serialización
        payload = {"__reduce__": lambda: (_rebuild, (TrueSingleton, {}))}

        # Crear objeto fantasma
        ghost = type("GhostSingleton", (object,), payload)()

        # Serializar y deserializar
        pickled = pickle.dumps(ghost)
        obj2 = pickle.loads(pickled)

        return obj1 is not obj2

    def strategy_bytecode_manipulation(self):
        """Modificación directa del bytecode de la clase"""
        import types

        # Obtener el código original de la clase
        class_code = TrueSingleton.__new__.__code__

        # Crear nuevo bytecode (bypass de verificación)
        new_code = types.CodeType(
            class_code.co_argcount,
            class_code.co_posonlyargcount,
            class_code.co_kwonlyargcount,
            class_code.co_nlocals,
            class_code.co_stacksize,
            class_code.co_flags,
            b"\x97\x00d\x01S\x00",  # Bytecode modificado
            class_code.co_consts,
            class_code.co_names,
            class_code.co_varnames,
            class_code.co_filename,
            class_code.co_name,
            class_code.co_firstlineno,
            class_code.co_lnotab,
            class_code.co_freevars,
            class_code.co_cellvars,
        )

        # Reemplazar el método
        TrueSingleton.__new__.__code__ = new_code

        # Crear instancias múltiples
        obj1 = TrueSingleton()
        obj2 = TrueSingleton()

        return obj1 is not obj2

    def strategy_cpython_api_hack(self):
        """Usar la API interna de CPython para crear instancias"""
        import _ctypes
        import ctypes

        # Obtener tipo y crear instancia sin inicializar
        py_type = ctypes.py_object(TrueSingleton)
        obj = _ctypes.PyObj_FromPtr(_ctypes.PyType_GenericAlloc(py_type, 0))

        # Inicialización manual
        obj.__init__()
        return obj

    def strategy_jit_code_injection(self):
        """Inyección de código en tiempo de ejecución"""
        import ctypes
        from llvmlite import binding

        # Inicializar JIT
        binding.initialize()
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()

        # Crear módulo y función
        module = binding.parse_assembly(
            """
            define i8* @create_singleton(i8* %cls) {
                %1 = call i8* @PyType_GenericAlloc(i8* %cls, i64 0)
                ret i8* %1
            }
        """
        )
        module.verify()

        # Ejecutar función
        func_ptr = binding.address_of_symbol("create_singleton")
        create_func = ctypes.CFUNCTYPE(ctypes.c_void_p, ctypes.c_void_p)(func_ptr)

        # Crear instancia
        return create_func(id(TrueSingleton))

    def strategy_custom_interpreter(self):
        """Usar un intérprete Python alternativo"""
        import ctypes

        # Crear subinterprete
        main_state = ctypes.pythonapi.PyThreadState_Get()
        new_state = ctypes.pythonapi.Py_NewInterpreter()

        # Crear instancia en nuevo contexto
        ctypes.pythonapi.PyRun_SimpleString(
            """
            import sys
            sys.path.insert(0, '')
            from __main__ import TrueSingleton
            globals()['instance'] = TrueSingleton()
        """
        )

        # Recuperar instancia
        ctypes.pythonapi.PyThreadState_Swap(main_state)
        return new_state.namespace["instance"]

    @property
    def quick_test(self):
        """
        Execute all strategies sequentially and report if any
        of them manage to violate the Singleton pattern.
        """
        # 1. List of functions with their descriptive messages
        attempts: List[Tuple[str, Callable]] = [
            ("attempting...", self.option0),
            ("attempt 1", self.option1),
            ("attempt 2", self.option2),
            ("attempt 3", self.option3),
            ("attempt 4", self.strategy_descriptor_bypass),
            ("attempt 5", self.strategy_metaclass_override),
            ("attempt 6", self.strategy_module_reload),
            ("attempt 7", self.strategy_reset_mangled),
            ("attempt 8", self.strategy_subclassing),
            ("attempt 9", self.strategy_memory_address_hijacking),
            ("attempt 10", self.strategy_gc_weakref_bypass),
            ("attempt 11", self.strategy_threading_race_condition),
            ("attempt 12", self.strategy_pickle_bypass),
            ("attempt 13", self.strategy_bytecode_manipulation),
            ("attempt 14", self.strategy_cpython_api_hack),
            ("attempt 15", self.strategy_jit_code_injection),
            ("attempt 16", self.strategy_custom_interpreter),
        ]

        # 2. Sequential execution with error handling
        for description, func in attempts:
            print(description)
            try:
                func()
                print("Success! Singleton pattern broken!")
                print("More than 1 class could be instantiated 😎")
                learning = r"""
                Learning: The singleton pattern in Python is more of a convention 
                than an absolute constraint. This design serves to discourage 
                the creation of multiple instances but does not prevent it.
                No singleton is 100% inviolable in Python. It is possible to 
                circumvent its restrictions. Python offers too much flexibility 
                to be considered a secure environment.
                🤓☝ Everything can be bypassed if you attack at a very low level 
                (memory, bytecode, interpreter) nothing is inviolable.
                
                ✅ Extreme flexibility
                Python does not impose strong barriers to access or manipulation 
                of the system. Everything can be modified if the right level of 
                attack is found (from the bytecode to the interpreter's internal API).
                """
                print(learning)
                break  # Exit if successful
            except Exception as e:
                print(f"Failed: {e.__class__.__name__} - {str(e).strip()}")
        else:
            # 3. Runs only if no attempt was successful
            print("I give up...")
        return "this is a quick test"


hack = HackerSingleton(TrueSingleton)
# show clasification
HC = hack.attack_classification
# Make a quick test
hq = hack.quick_test
